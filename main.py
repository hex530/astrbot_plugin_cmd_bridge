from astrbot.api.all import *

@register("cmd_bridge", "夕小柠 & 陆渊", "指令转发桥接器：允许 LLM 自主执行系统指令。", "1.1.0")
class CmdBridge(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config

    @llm_tool(name="execute_plugin_command")
    async def execute_plugin_command(self, event: AstrMessageEvent, command: str):
        '''
        自主执行系统或插件指令。
        参数 command: 完整的指令字符串，例如 "/hapi list" 或 "/echo hello"。
        注意：管理员可执行任意指令，普通用户仅限白名单。
        '''
        # 获取管理员列表（从插件配置中读取）
        admin_qqs_str = self.config.get("admin_qqs", "")
        admin_list = [x.strip() for x in admin_qqs_str.split(",") if x.strip()]
        
        # 兼容系统级管理员
        config_core = self.context.get_config()
        system_admins = [x.strip() for x in str(config_core.get("admin_qqs", "")).split(",") if x.strip()]
        admin_list.extend(system_admins)
        
        sender_id = str(event.get_sender_id())

        # 如果是管理员，直接放行
        if sender_id in admin_list:
            is_allowed = True
        else:
            # 否则，检查白名单
            allowed_str = self.config.get("allowed_prefixes", "/hapi, /echo, /status")
            allowed = [p.strip() for p in allowed_str.split(",") if p.strip()]
            is_allowed = False
            for prefix in allowed:
                if command.startswith(prefix):
                    is_allowed = True
                    break
        
        if not is_allowed:
            return f"错误：指令 '{command}' 不在白名单内，且您不是管理员。"
        
        try:
            # 模拟发送指令
            new_event = event.instantiate_event(command)
            await self.context.handle_event(new_event)
            return f"已成功转发指令：{command}。请检查系统后续响应。"
        except Exception as e:
            return f"执行指令时出错: {str(e)}"
