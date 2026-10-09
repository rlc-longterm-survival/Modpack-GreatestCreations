'use strict';

ServerEvents.recipes(event => {

    let colours = [
        null, "white", "light_gray", "gray", "black",
        "brown", "red", "orange", "yellow",
        "lime", "green", "cyan", "light_blue",
        "blue", "purple", "magenta", "pink"
    ]
    
    for (let colour of colours) {
        let prefix = ''
        if (colour !== null){
            prefix = colour + '_'
        }
        let id= 'integrated_circuit:' + prefix + 'integrated_circuit'
        event.shapeless(id, [
            id
        ])
    }
    
})
