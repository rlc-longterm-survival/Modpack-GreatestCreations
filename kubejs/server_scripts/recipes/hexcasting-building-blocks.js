// Recipe for Hex Casting 1.20 building blocks.
// Why didn't petrak add recipes?

ServerEvents.recipes(event => {
  // Recipes for basic tiles
  event.remove({output: Item.of('hexcasting:amethyst_tiles')})
  event.shaped(Item.of('9x hexcasting:amethyst_tiles'), [
    'BBB',
    'BDB',
    'BBB'
  ], {
    B: 'minecraft:amethyst_block',
    D: 'hexcasting:amethyst_dust'
  })
  event.shaped(Item.of('9x hexcasting:quenched_allay_tiles'), [
    'BBB',
    'BDB',
    'BBB'
  ], {
    B: Item.of('hexcasting:quenched_allay'),
    D: 'hexcasting:amethyst_dust'
  })
  event.shaped(Item.of('9x hexcasting:slate_tiles'), [
    'BBB',
    'BDB',
    'BBB'
  ], {
    B: Item.of('hexcasting:slate_block'),
    D: 'hexcasting:amethyst_dust'
  })

  // Recipe for mixed tile
  event.shapeless(Item.of('2x hexcasting:slate_amethyst_tiles'), [
    Item.of('hexcasting:slate_tiles'),
    Item.of('hexcasting:amethyst_tiles')
  ])

  // Arbitrary transition by stonecutting
  function stoneCuttingTransition(items) {
    for(let src of items) {
      for(let dest of items) {
        event.stonecutting(dest, src);
      }
    }
  }
  stoneCuttingTransition([
    Item.of('hexcasting:quenched_allay_tiles'),
    Item.of('hexcasting:quenched_allay_bricks'),
    Item.of('hexcasting:quenched_allay_bricks_small'),
  ])
  stoneCuttingTransition([
    Item.of('hexcasting:amethyst_tiles'),
    Item.of('hexcasting:amethyst_bricks'),
    Item.of('hexcasting:amethyst_bricks_small'),
    Item.of('hexcasting:amethyst_pillar'),
  ])
  stoneCuttingTransition([
    Item.of('hexcasting:slate_tiles'),
    Item.of('hexcasting:slate_bricks'),
    Item.of('hexcasting:slate_bricks_small'),
    Item.of('hexcasting:slate_pillar'),
  ])
  stoneCuttingTransition([
    Item.of('hexcasting:slate_amethyst_tiles'),
    Item.of('hexcasting:slate_amethyst_bricks'),
    Item.of('hexcasting:slate_amethyst_bricks_small'),
    Item.of('hexcasting:slate_amethyst_pillar'),
  ])
})
