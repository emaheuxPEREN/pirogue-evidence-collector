import "./friTap/agent/ssl_log.js";
import { log_ad_ids } from "./pirogue/log_ad_ids.js";
import { log_aes_info } from "./pirogue/log_aes_info.js";
import { socket_trace } from "./pirogue/log_socket_operations.js";
import  { no_root } from "./pirogue/no_root.js";
import  { inject_hooks } from "./pirogue/dynamic_hook_injector.js";

rpc.exports['logAdIds'] = log_ad_ids;
rpc.exports['log_ad_ids'] = log_ad_ids;
rpc.exports['logAesInfo'] = log_aes_info;
rpc.exports['log_aes_info'] = log_aes_info;
rpc.exports['socketTrace'] = socket_trace;
rpc.exports['socket_trace'] = socket_trace;
rpc.exports['noRoot'] = no_root;
rpc.exports['no_root'] = no_root;
rpc.exports['injectDynamicHooks'] = inject_hooks;
rpc.exports['inject_dynamic_hooks'] = inject_hooks;
