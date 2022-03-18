from discord.ext.commands import command, Cog, errors
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

import re
import multiprocess
import RestrictedPython
from RestrictedPython import compile_restricted, limited_builtins, safe_builtins, utility_builtins
from RestrictedPython.PrintCollector import PrintCollector


def interpret(code):
    """Interprets the given python code inside a safe execution environment"""
    code += "\nresults = printed"
    byte_code = compile_restricted(
        code,
        filename="<string>",
        mode="exec",
    )
    data = {
        "_print_": PrintCollector,
        "__builtins__": {
            **limited_builtins,
            **safe_builtins,
            **utility_builtins,
            "all": all,
            "any": any,
            "_getiter_": RestrictedPython.Eval.default_guarded_getiter,
            "_iter_unpack_sequence_": RestrictedPython.Guards.guarded_iter_unpack_sequence
        },
        "_getattr_": RestrictedPython.Guards.safer_getattr
    }
    exec(byte_code, data, None)
    return data["results"]


class Inter(Cog, name='Hots'):
    """
    — Интерпретатор кода на python
    """
    def __init__(self, bot):
        self.bot = bot

    @command(name=">>")
    async def interpreter(self, ctx):
        message = ctx.message
        command_str = "!>>"
        content = message.content
        source = re.sub(r"{} ?".format(command_str), "", content, 1)
        # remove code markers so code boxes work with this "beautiful" regex
        source = re.sub(r"(^`{1,3}(py(thon)?)?|`{1,3}$)", "", source)
        # log output to help debugging on failure
        print("Executed {}".format(repr(source)))
        sent = await message.channel.send("running code...")
        try:
            result = interpret(source)
            output = result
        except multiprocess.context.TimeoutError:
            output = "Timeout error - do you have an infinite loop?"
        except Exception as e:
            output = "Runtime error: {}".format(e)
        await sent.edit(content="```\n{}```".format(output or "(no output to stdout)"))


def setup(bot):
    DiscordComponents(bot)  # If you have this in an on_ready() event you can remove this line.
    bot.add_cog(Inter(bot))