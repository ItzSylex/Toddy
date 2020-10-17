import constants

shop = [
    {
        "name": "Alimento",
        "price": 120,
        "description": "Comida para tu mascota, esta rica",
        "emoji": "<:food:766492241966661663>",
        "file_code": "food",
        "longer_description": ""
    },
    {
        "name": "Rifle de patos",
        "price": 20000,
        "description": "Necesario para poder salir a cazar",
        "emoji": "<:rifle:766492242604851261>",
        "file_code": "rifle",
        "longer_description": ""
    },
    {
        "name": "Galleta",
        "price": 50,
        "description": "Puede ser un regalo",
        "emoji": "<:cookie:766492137725886464>",
        "file_code": "cookie",
        "longer_description": ""
    },
    {
        "name": "Medalla de oro",
        "price": 40000,
        "description": "No hace nada, presume",
        "emoji": "<:gold_medal:766492138870800384>",
        "file_code": "gold_medal",
        "longer_description": ""
    },
    {
        "name": "Medalla de plata",
        "price": 35000,
        "description": "No hace nada, presume",
        "emoji": "<:silver_medal:766492138510483508>",
        "file_code": "silver_medal",
        "longer_description": ""
    },
    {
        "name": "Medalla de bronce",
        "price": 20000,
        "description": "No hace nada, es de bronce",
        "emoji": "<:bronze_medal:766492136970387496>",
        "file_code": "bronze_medal",
        "longer_description": ""
    },
    {
        "name": "Telefono",
        "price": 6000,
        "description": "Usala para poner un estado",
        "emoji": "<:cellphone:766492137051127829>",
        "file_code": "cellphone",
        "longer_description": ""
    },
    {
        "name": "Laptop",
        "price": 10000,
        "description": "Con esto podras jugar y ganar mas quacks",
        "emoji": "<:laptop:766492138573266975>",
        "file_code": "laptop",
        "longer_description": ""
    },
    {
        "name": "Carro",
        "price": 100000,
        "description": "No se, es un carro",
        "emoji": "<:car:766492513044267028>",
        "file_code": "car",
        "longer_description": ""
    },
    {
        "name": "Caña de pescar",
        "price": 20000,
        "description": "Usala para irte a pescar y ganar unos quacks",
        "emoji": "<:fishing:766615393066287145>",
        "file_code": "fishing",
        "longer_description": ""
    },
    {
        "name": "Municion x10",
        "price": 500,
        "description": "Necesitas muncion para poder usar tu rifle de casa",
        "emoji": "<:ammo:766615392583548938>",
        "file_code": "ammo",
        "longer_description": ""
    },
    {
        "name": "Cebo x10",
        "price": 500,
        "description": "Lo necesitaras para ir a pescar",
        "emoji": "<:bait:766615392940326912>",
        "file_code": "bait",
        "longer_description": ""
    },
    {
        "name": "Fragmento de llave comun",
        "price": 600,
        "description": "Usalo para craftear una llave comun, necesitaras al menos 4",
        "emoji": "<:com_frag:766757065422536708>",
        "file_code": "com_frag",
        "longer_description": ""
    },
    {
        "name": "Fragmento de llave epica",
        "price": 2400,
        "description": "Usalo para craftear una llave epica, necesitaras al menos 4",
        "emoji": "<:epic_frag:766757065493315636>",
        "file_code": "epic_frag",
        "longer_description": ""
    },
    {
        "name": "Fragmento de llave legendaria",
        "price": 5000,
        "description": "Usalo para craftear una llave legendaria, necesitaras al menos 4",
        "emoji": "<:legen_frag:766757065968058470>",
        "file_code": "legen_frag",
        "longer_description": ""
    },
    {
        "name": "Caja comun",
        "price": 500,
        "description": "Abrela! Tiene cosas interesantes",
        "emoji": "<:com_crate:766615392826294286>",
        "file_code": "com_crate",
        "longer_description": ""
    },
    {
        "name": "Caja epica",
        "price": 500,
        "description": "Abrela para obtener quacks o hasta un item legendario",
        "emoji": "<:epic_crate:766615392943603744>",
        "file_code": "epic_crate",
        "longer_description": ""
    },
    {
        "name": "Caja legendaria",
        "price": 600,
        "description": "Abrela! Podras obtener muchos quacks o un item legendario",
        "emoji": "<:legen_crate:766615393656635402>",
        "file_code": "legen_crate",
        "longer_description": ""
    },
]

NOTHING_RESPONSE = [
    f"{constants.x} No has encontrado **nada**.",
    f"{constants.x} Esto esta **vacio**.",
    f"{constants.x} Intentalo mas tarde, no hay **nada**.",
    f"{constants.x} **Nada** por aca, **nada** por allá.",
    f"{constants.x} No encontraste **nada** interesante.",
]

FOUND_RESPONSE = [
    f"{constants.check} Mira encontraste VAR **quacks**.",
    f"{constants.check} Que suerte, aca tienes VAR **quacks**.",
    f"{constants.check} Recibiste VAR **quacks**.",
    f"{constants.check} VAR **quacks**, ok.",
    f"{constants.check} Desgraciadamente econtraste VAR **quacks**"
]

BEG_RESPONSE = [
    f"{constants.check} Sorprendentemente alguien te dio VAR **quacks**.",
    f"{constants.check} Te dieron VAR **quacks** por lastima, deja de pedir.",
    f"{constants.check} Recibiste VAR **quacks**.",
    f"{constants.check} Te tiraron VAR **quacks**.",
    f"{constants.check} Alguien te dio VAR **quacks**.",
]

BEG_NO_RESPONSE = [
    f"{constants.x} Te miraron mal y no te dieron **nada**.",
    f"{constants.x} Nope, **nada**.",
    f"{constants.x} Que **verguenza**, mejor pide despues.",
    f"{constants.x} Obtuviste; **nada**.",
    f"{constants.x} No te dieron **nada**.",
]
