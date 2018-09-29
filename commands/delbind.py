from discord import Embed
from discord.utils import find

from resources.module import get_module
get_group = get_module("roblox", attrs=["get_group"])

async def setup(**kwargs):
	command = kwargs.get("command")
	r = kwargs.get("r")

	@command(name="delbind", category="Binds", permissions={
		"raw": "manage_guild"
	}, aliases=["delbinds", "deletebind", "deletebinds"], arguments=[
		{
			"prompt": "Please specify the group ID that this bind resides in.",
			"type": "number",
			"name": "group"
		},
		{
			"prompt": "Either specify the rank ID/all to delete that individual binding, " \
				"or say ``everything`` to clear all bindings for that group.",
			"type": "string",
			"name": "rank"
		}
	])
	async def delbind(message, response, args, prefix):
		"""deletes a group bind"""

		guild = message.guild

		guild_data = await r.table("guilds").get(str(guild.id)).run() or {}
		role_binds = guild_data.get("roleBinds") or {}

		if not role_binds:
			return await response.error("You have no binds! Say ``!bind`` to make a new bind.")

		group_id = str(args.parsed_args["group"])
		rank = args.parsed_args["rank"]

		is_num = False

		try:
			int(rank)
			is_num = True
		except ValueError:
			pass

		if not role_binds.get(group_id):
			return await response.error("A bind for this group ID does not exist.")

		if ((is_num and rank != "0") or rank == "all" or ""):
			if not role_binds.get(group_id, {}).get(rank):
				return await response.error("A binding with this group/rank combination does not exist.")

			role_binds[group_id].pop(rank, None)
			guild_data["roleBinds"] = role_binds

			await r.table("guilds").insert({
				**guild_data
			}, conflict="replace").run()

			return await response.success("Successfully **deleted** this bind.")

		elif rank == "guest" or rank == "0":
			if not role_binds.get(group_id, {}).get("guest") and not role_binds.get(group_id, {}).get("0"):
				return await response.error("A binding with this group/rank combination does not exist.")

			rank = rank = "guest" and "0"

			role_binds[group_id].pop(rank, None)
			guild_data["roleBinds"] = role_binds

			await r.table("guilds").insert({
				**guild_data
			}, conflict="replace").run()

			return await response.success("Successfully **deleted** this bind.")
		elif rank == "everything":
			if not role_binds.get(group_id):
				return await response.error("A bind for this group does not exist.")

			role_binds.pop(group_id, None)
			guild_data["roleBinds"] = role_binds

			await r.table("guilds").insert({
				**guild_data
			}, conflict="replace").run()

			await response.success("Successfully **deleted** this bind.")
		else:
			await response.error("Invalid rank choice.")


