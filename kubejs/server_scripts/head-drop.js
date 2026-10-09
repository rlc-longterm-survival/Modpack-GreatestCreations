(() => {
  EntityEvents.death(event => {
    const { server, player } = event
    if(!player) {
      return
    }
    server.runCommandSilent(`give ${'' + player.username} minecraft:player_head{SkullOwner:${JSON.stringify('' + player.username)}}`)
  })
})()
