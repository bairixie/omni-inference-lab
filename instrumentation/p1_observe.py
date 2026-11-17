"""P3 request/batch/process observations in RAM, exported only between cohorts.

No shared current request, file IO, reset of CUDA peaks, device synchronizations,
or changes to scheduling. Existing P1 hook module name retained for compatibility.
"""
import collections
import importlib.metadata
import inspect
import os
import time
import torch

RUN_ID=os.environ.get('P3_RUN_ID','unknown')
requests={}
completed_requests={}
native_events={}
pool_layouts={}
tokenizers={}
batches=[]
pending_batches=collections.defaultdict(collections.deque)
processing_batch={}
active_requests=set()
sequence=0

def clocks():
    return {'timestamp_ns':time.time_ns(),'monotonic_ns':time.monotonic_ns()}

def ensure(identifier):
    if identifier not in requests:
        value={'run_id':RUN_ID,'request_id':identifier,'window_id':identifier.split('__')[1] if '__' in identifier else 'unknown',
               'pid':os.getpid(),'status':'observed','max_kv_allocated_slots':0,'max_kv_committed_slots':0,
               'batch_ids':[],'last_output_count':0,'first_generated':None,'last_generated':None,
               'first_text_observed':None,'last_text_observed':None,'text_token_count':0,
               'prefill_launches':0,'decode_launches':0,'token_observations':[],
               'native_events':native_events.setdefault(identifier,[])}
        requests.setdefault(identifier,value)
    return requests[identifier]

def native_event(identifier,stage,event_name,timestamp_ns=None):
    if not os.environ.get('P3_RUN_ID') or not identifier:
        return
    state=ensure(identifier);now=clocks()
    state['native_events'].append({'run_id':RUN_ID,'request_id':identifier,'stage':stage,'event_name':event_name,
          'timestamp_ns':timestamp_ns if timestamp_ns is not None else now['timestamp_ns'],
          'monotonic_ns_at_hook':now['monotonic_ns'],'pid':os.getpid()})

def begin(identifier):
    state=ensure(identifier);state['begin']=clocks();state['status']='started';active_requests.add(identifier)

def failed(identifier,where,exc):
    state=ensure(identifier);state['status']='failed';state['failure']={'where':where,'type':type(exc).__name__,'message':str(exc),**clocks()};active_requests.discard(identifier)

def preprocess(identifier,audios,processed,tokenizer=None):
    state=ensure(identifier)
    if tokenizer is not None: tokenizers[identifier]=tokenizer
    bounds=processed['audio_bounds'][0];lengths=processed['audio_feature_lens'][0];ids=processed['input_ids'][0]
    assert all(x.device.type=='cpu' for x in [bounds,lengths,ids])
    state['input']={'decoded_samples':[len(x) for x in audios],'decoded_sample_rate_hz':16000,
       'input_positions':ids.numel(),'audio_bounds':bounds.tolist(),'feature_lengths':lengths.tolist(),
       'audio_features_shape':list(processed['audio_features'].shape)}
    state['preprocessing_accounted']=clocks()

def encoder_begin(identifier,stage_name):
    ensure(identifier)['encoder_start']=clocks()

def encoder_end(identifier,stage_name,output,cache,hit):
    state=ensure(identifier);state['encoder_end']=clocks()
    state['encoder']={'stage':stage_name,'output_shapes':{k:list(v.shape) for k,v in output.items() if isinstance(v,torch.Tensor)},
        'cache_hit':hit,'cache_entries':len(cache.cache),'cache_bytes':cache.current_bytes,'cache_evictions':cache.eviction_count}

def memory():
    return {'torch_allocated_bytes':torch.cuda.memory_allocated(),'torch_reserved_bytes':torch.cuda.memory_reserved(),
            'torch_peak_allocated_bytes':torch.cuda.max_memory_allocated(),'torch_peak_reserved_bytes':torch.cuda.max_memory_reserved()}

def pool_state(scheduler):
    a=scheduler.token_to_kv_pool_allocator
    return {'capacity_slots':a.size,'free_slots':a.available_size(),'pool_unavailable_slots':a.size-a.available_size(),
            'page_size_tokens':a.page_size,'deferred_free_slots':sum(t.numel()*a.page_size for t in a.free_group or []),
            'prefix_evictable_slots':scheduler.tree_cache.evictable_size(),'prefix_protected_slots':scheduler.tree_cache.protected_size(),
            'scheduler_retractions':scheduler.num_retracted_reqs,'waiting_queue_size':len(scheduler.waiting_queue),
            'running_batch_size':len(scheduler.running_batch.reqs),'active_observed_requests':len(active_requests)}

def scheduler_memory(scheduler):
    allocator=scheduler.token_to_kv_pool_allocator;cache=allocator.get_kvcache();identity=id(allocator)
    if identity not in pool_layouts:
        tensors=cache.k_buffer+cache.v_buffer
        storages={t.untyped_storage().data_ptr():t.untyped_storage().nbytes() for t in tensors}
        pool_layouts[identity]={'allocator_class':type(allocator).__name__,'pool_class':type(cache).__name__,
              'kv_storage_bytes':sum(storages.values()),'kv_bytes_per_slot':sum(t[0].numel()*t.element_size() for t in tensors),
              'kv_tensor_count':len(tensors),'kv_dtype':str(tensors[0].dtype),'torch_version':torch.__version__,
              'sglang_version':importlib.metadata.version('sglang')}
    return {**pool_layouts[identity],**pool_state(scheduler),'requests':requests,'completed_requests':completed_requests,
            'batch_records':batches,'unmatched_pending_batch_ids':{str(k):list(v) for k,v in pending_batches.items() if v},
            'pid':os.getpid(),'scheduler_source':inspect.getfile(type(scheduler)),**memory()}

def req_counts(req):
    return {'request_id':req.rid,'input_positions':len(req.origin_input_ids),'output_tokens':len(req.output_ids),
            'kv_allocated_slots':req.kv.kv_allocated_len,'kv_committed_slots':req.kv.kv_committed_len,
            'retraction_count':req.retraction_count}

def batch(scheduler,batch,boundary):
    global sequence
    key=(id(scheduler),id(batch));now=clocks()
    if boundary in ['launch','async_launch']:
        sequence+=1;bid=f'{RUN_ID}:{os.getpid()}:{sequence}'
        data={'run_id':RUN_ID,'batch_id':bid,'pid':os.getpid(),'forward_mode':str(batch.forward_mode),
              'is_decode':batch.forward_mode.is_decode(),'batch_size':len(batch.reqs),
              'request_ids':[r.rid for r in batch.reqs],'launch':now,'launch_boundary':boundary,
              'launch_requests':[req_counts(r) for r in batch.reqs],'launch_pool':pool_state(scheduler)}
        batches.append(data);pending_batches[key].append(len(batches)-1)
        for req in batch.reqs:
            state=ensure(req.rid);state['batch_ids'].append(bid)
            state['decode_launches' if batch.forward_mode.is_decode() else 'prefill_launches']+=1
    else:
        if not pending_batches[key]:
            raise RuntimeError('P3 instrumentation: result batch has no launch identity')
        index=pending_batches[key].popleft();data=batches[index];data['result_ready']=now
        data['result_requests']=[req_counts(r) for r in batch.reqs];data['result_pool']=pool_state(scheduler)
        processing_batch[id(scheduler)]=index
    for req in batch.reqs:
        state=ensure(req.rid)
        state['max_kv_allocated_slots']=max(state['max_kv_allocated_slots'],req.kv.kv_allocated_len)
        state['max_kv_committed_slots']=max(state['max_kv_committed_slots'],req.kv.kv_committed_len)
        state['capacity_slots']=scheduler.token_to_kv_pool_allocator.size
        state['page_size_tokens']=scheduler.token_to_kv_pool_allocator.page_size

def batch_result_done(scheduler,batch):
    index=processing_batch.pop(id(scheduler),None)
    if index is not None:
        batches[index]['cleanup_done']=clocks();batches[index]['cleanup_pool']=pool_state(scheduler)

def tokens_observed(scheduler,req):
    state=ensure(req.rid);count=len(req.output_ids);previous=state['last_output_count']
    if count<=previous:return
    now=clocks();index=processing_batch.get(id(scheduler));bid=batches[index]['batch_id'] if index is not None else None
    if state['first_generated'] is None:
        state['first_generated']={**now,'output_index_1based':previous+1,'token_id':req.output_ids[previous]}
    tokenizer=tokenizers.get(req.rid)
    if tokenizer is not None:
        for offset in range(previous,count):
            token_id=req.output_ids[offset];piece=tokenizer.decode([token_id],skip_special_tokens=True)
            if piece.strip():
                stamp={**now,'output_index_1based':offset+1,'token_id':token_id,'piece':piece}
                if state['first_text_observed'] is None:state['first_text_observed']=stamp
                state['last_text_observed']=stamp;state['text_token_count']+=1
    else:state['text_boundary_error']='request tokenizer unavailable'
    state['last_generated']={**now,'output_index_1based':count,'token_id':req.output_ids[-1]}
    state['last_output_count']=count
    # Lightweight per-step clocks support request/batch correlation in all modes.
    state['token_observations'].append({**now,'output_count':count,'batch_id':bid})

def terminal(scheduler,req):
    state=ensure(req.rid);state['terminal']=clocks();state['terminal_pool']=pool_state(scheduler)
    state['status']='generation_finished';active_requests.discard(req.rid)
    completed_requests[req.rid]={'run_id':RUN_ID,'request_class':type(req).__name__,'retraction_count':req.retraction_count,
        'origin_positions':len(req.origin_input_ids),'output_tokens':len(req.output_ids),'output_ids':list(req.output_ids),
        'finished_reason':req.finished_reason.to_json() if req.finished_reason is not None else None,'measurement':state}

def finish(identifier,result):
    state=ensure(identifier);state['text_result_ready']=clocks();state['usage']=result.get('usage');state['finish_reason']=result.get('finish_reason');state['status']='completed';active_requests.discard(identifier)

def release(scheduler,req,boundary):
    ensure(req.rid).setdefault('release_events',[]).append({'boundary':boundary,'retraction_count':req.retraction_count,**clocks()})
