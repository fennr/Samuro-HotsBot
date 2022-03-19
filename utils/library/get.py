def author(ctx):
    try:
        return ctx.message.author.name
    except AttributeError:
        return ctx.author


def author_id(ctx):
    try:
        return ctx.message.author.id
    except AttributeError:
        return ctx.author_id


def guild_name(ctx):
    if ctx.guild is None:
        return ''
    else:
        try:
            return ctx.guild.name
        except AttributeError:
            return ctx.guild


def guild_id(ctx):
    if ctx.guild is None:
        return ''
    else:
        try:
            return ctx.message.guild.id
        except AttributeError:
            return ctx.guild_id


