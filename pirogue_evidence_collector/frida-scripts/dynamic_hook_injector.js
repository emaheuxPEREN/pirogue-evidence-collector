"use strict";

function _inject_hooks(pid, process, hook_list) {
    hook_list.forEach(item => {
        console.log(item);
        item.methods.forEach(method => {
            try {
                const name_split = method.split('/');
                const class_name = name_split.slice(0, -1).join('/').slice(1);
                const method_name = name_split[name_split.length - 1];
                if (method.startsWith('L')) {
                    try {
                        _inject_hook(pid, process, item.taxonomy_id, item.description, class_name, method_name);
                    } catch (error) {
                        console.log({
                            message_type: "java_hook_error",
                            class: class_name,
                            method: method_name,
                            error_message: error,
                        });
                    }
                }
            } catch (error) {
                console.log({
                    message_type: "hook_error", name: method, error_message: error,
                });
            }
        });
    });
}

function _inject_hook(pid, process, taxonomy_id, description, class_name, method_name) {
    function _send_msg(msg) {
        const _msg = {
            message_type: "java_hook_data",
            type: 'dynamic_hook_log',
            dump: 'dynamic_hook.json',
            data_type: 'json',
            pid: pid,
            process: process,
            timestamp: Date.now(),
            data: msg
        }
        send(_msg)
    }

    const target_class = Java.use(class_name);
    const overloads = target_class[method_name].overloads;
    const Exception = Java.use('java.lang.Exception');
    // hook each method's overloads
    overloads.forEach(overload => {
        overload.implementation = function () {
            const timestamp = Date.now();
            try {
                const args = [].slice.call(arguments);
                const returned_value = this[method_name].apply(this, arguments);
                const stacktrace = Exception.$new().getStackTrace().toString().split(',');
                _send_msg({
                    taxonomy_id: taxonomy_id,
                    description: description,
                    timestamp: timestamp,
                    class: target_class.$className,
                    method: method_name,
                    arguments: args,
                    returned_value: returned_value ? returned_value : null,
                    stacktrace: stacktrace
                });
                return returned_value;
            } catch (error) {
                console.log({
                    message_type: "java_hook_data_error",
                    timestamp: timestamp,
                    class: class_name,
                    method: method_name,
                    error_message: error
                });
            }
        };
    });
}

function inject_hooks(pid, process, hook_list) {
    Java.perform(() => {
        _inject_hooks(pid, process, hook_list);
    });
}

try {
    r2frida.pluginRegister('inject_dynamic_hooks', inject_hooks);
} catch (e) {
}

try {
    rpc.exports['injectDynamicHooks'] = inject_hooks;
} catch (e) {
}