

def get_player_id(request): 
    _meta       = request.META  
    _real_ip    = _meta.get('HTTP_X_REAL_IP','')
    _forwarded_server = _meta.get('HTTP_X_FORWARDED_SERVER','')
    _remote_addr = _meta.get('REMOTE_ADDR','')
    _mobile     = _meta.get('HTTP_SEC_CH_UA_MOBILE','')
    _platform   = _meta.get('HTTP_SEC_CH_UA_PLATFORM','')
    _session_id = _meta.get('HTTP_USER_AGENT','HTTP_USER_AGENT')
    _session_id = _session_id.replace(' ','_').replace('"','').replace('(','').replace(')','').replace('/','').replace('\\','').replace(';','').replace(',','_').replace('.','_').strip()
    
    _player_id = '_'.join([_real_ip,_forwarded_server,_remote_addr,_mobile,_platform,_session_id])
    _player_id = _player_id.replace(' ','_').replace('"','').replace('(','').replace(')','').replace('/','').replace('\\','').replace(';','').replace(',','_').replace('.','_').strip()
    return _player_id,_remote_addr,_session_id