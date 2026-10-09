// Applies more expensive create-styled recipes for advanced drawers.
// In exchange, make drawer equipments wrench-pickable.
// Inspired by https://modrinth.com/datapack/storage-drawers-create-compat/gallery

ServerEvents.recipes(event => {
  // Compacting Drawers (2-Tier)
  event.remove({output: Item.of('storagedrawers:compacting_drawers_2')})
  event.shaped(Item.of('storagedrawers:compacting_drawers_2'), [
    'SCS',
    'SDS',
    'SIS'
  ], {
    S: 'minecraft:stone',
    C: 'create:mechanical_crafter',
    D: '#storagedrawers:full_drawers',
    I: 'create:iron_sheet'
  })
  event.remove({output: Item.of('storagedrawers:compacting_half_drawers_2')})
  event.shaped(Item.of('storagedrawers:compacting_half_drawers_2'), [
    'SCS',
    'SDS',
    'SIS'
  ], {
    S: 'minecraft:stone',
    C: 'create:mechanical_crafter',
    D: '#storagedrawers:half_drawers',
    I: 'create:iron_sheet'
  })

  // Compacting Drawers (3-Tier)
  event.remove({output: Item.of('storagedrawers:compacting_drawers_3')})
  event.shaped(Item.of('storagedrawers:compacting_drawers_3'), [
    'SSS',
    'CDC',
    'SIS'
  ], {
    S: 'minecraft:stone',
    C: 'create:mechanical_crafter',
    D: '#storagedrawers:full_drawers',
    I: 'create:iron_sheet'
  })
  event.remove({output: Item.of('storagedrawers:compacting_half_drawers_3')})
  event.shaped(Item.of('storagedrawers:compacting_half_drawers_3'), [
    'SSS',
    'CDC',
    'SIS'
  ], {
    S: 'minecraft:stone',
    C: 'create:mechanical_crafter',
    D: '#storagedrawers:half_drawers',
    I: 'create:iron_sheet'
  })

  // Controller
  event.remove({output: Item.of('storagedrawers:controller')})
  event.shaped(Item.of('storagedrawers:controller'), [
    'SCS',
    'EDE',
    'SBS'
  ], {
    S: 'minecraft:stone',
    C: 'create:chute',
    E: 'create:electron_tube',
    D: '#storagedrawers:drawers',
    B: 'create:brass_sheet'
  })
  event.remove({output: Item.of('storagedrawers:controller_slave')})
  event.shaped(Item.of('storagedrawers:controller_slave'), [
    'SCS',
    'IDI',
    'SIS'
  ], {
    S: 'minecraft:stone',
    C: 'create:chute',
    I: 'create:iron_sheet',
    D: '#storagedrawers:drawers',
  })
})

ServerEvents.tags('block', event => {
  event.add('create:wrench_pickup', /^storagedrawers:.*$/)
  event.remove('create:wrench_pickup', 'storagedrawers:framing_table')
})
