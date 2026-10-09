(() => {
  // ===== 快捷命令 =====
  ServerEvents.commandRegistry(event => {
    const { commands: Commands, arguments: Arguments } = event
    event.register(
      Commands
      .literal('runle')
      .requires(src => src.hasPermission(4))
      .then(Commands.literal('stop')
        .executes(ctx => {
          const server = ctx.source.server
          for(const player of server.getPlayers()) {
            player.kick('[Server] runle')
          }
          server.runCommandSilent('stop')
          return 1
        })
      )
      .then(Commands.literal('timer')
        .then(
          Commands.argument('seconds', Arguments.INTEGER.create(event).integer(0, 3600))
          .executes(ctx => {
            const seconds = Arguments.INTEGER.getResult(ctx, 'seconds')
            const server = ctx.source.server
            countDown = seconds * 20 + 20
            server.runCommandSilent('say Get ready to run!')
            return 1
          })
        )
      )
      .then(Commands.literal('cancel')
        .executes(ctx => {
          const server = ctx.source.server
          countDown = undefined
          server.runCommandSilent('say Runle countdown canceled.')
          return 1
        })
      )
    )
  })

  // ===== 倒计时 =====
  let countDown = undefined
  ServerEvents.tick(event => {
    const { player, server, message } = event

    if(countDown === undefined) {
      return
    }
    countDown -= 1
    if(countDown > 0 && countDown % 20 == 0) {
      server.runCommandSilent('say ' + (countDown / 20))
    }
    if(countDown == 0) {
      for(const player of server.getPlayers()) {
        player.kick('[Server] runle')
      }
      server.runCommandSilent('stop')
    }
  })
})()
