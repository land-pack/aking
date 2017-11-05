from aking.core import AKG

akg = AKG()


@akg.dispatch("user_join")
def user_join(handler, data):
    handler.write_messgge("")

@akg.sub("YourGameMessage")
def game_message(channel, data):
    some_players = data.get("players")
    some_content = data.get("content")
    akg.to_all(content)
    akg.to_part(content)



if __name__ == '__main__':
    akg.run()
