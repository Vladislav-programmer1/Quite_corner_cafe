//import { YMap, YMapDefaultSchemeLayer } from './lib/ymaps.js'
//
//const map = new YMap(
//    document.getElementById('map'),
//    {
//        location: {
//              center: [37.588144, 55.733842],
//              zoom: 10
//        }
//    }
//);
//
//map.addChild(new YMapDefaultSchemeLayer());
async function initMap() {
    await ymaps3.ready;

    const {YMap, YMapDefaultSchemeLayer} = ymaps3;

    const map = new YMap(
        document.getElementById('app'),
        {
            location: {
                center: [38.910562, 45.035267],
                zoom: 10
            }
        }
    );

    map.addChild(new YMapDefaultSchemeLayer());
}

initMap();