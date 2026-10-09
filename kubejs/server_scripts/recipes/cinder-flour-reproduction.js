ServerEvents.recipes(event => {
    event.recipes.createCompacting('minecraft:netherrack', [
        '1x create:cinder_flour',
        Fluid.of('minecraft:lava', 250)
    ])
})
