# Fuentes

Reproducciones bajadas de Wikimedia Commons el 2026-11-16. La licencia es la que declara Commons para
cada archivo; no se verificó de forma independiente. Las pinturas son de autores muertos hace más de 400 años.

| Caso | Archivo local | Archivo en Commons | Licencia declarada | Tamaño | SHA-256 |
|---|---|---|---|---|---|
| `julio2` | `julio2__rafael-1511__commons.jpg` | `File:Pope Julius II.jpg` | Public domain | 3111×4227 | `2bad12ee07017bd8ca74853586751b8bbdd4cd739124de4935e036475d5b73a2` |
| `prato` | `prato__rafael-1505__commons.jpg` | `File:Raphael - Madonna in the Meadow - Google Art Project.jpg` | Public domain | 6116×7832 | `1bc22ec379fe5e1f81207dcab0eee7e9d607fd1a94e0007aa77c239fc0bc0b9f` |
| `arnolfini` | `arnolfini__vaneyck-1434__commons.jpg` | `File:Van Eyck - Arnolfini Portrait.jpg` | Public domain | 4386×6000 | `8f36d6ec3f9c7355d74d8136d401dec704a0067797dee809c9dda485486bfed5` |
| `baco` | `baco__tiziano-1520__commons.jpg` | `File:Titian Bacchus and Ariadne.jpg` | Public domain | 4670×4226 | `9ec895e2010187948b8aa6a699bc1f3b27519b7fc4e9c98762befccea054fbb6` |
| `atenas` | `atenas__rafael-1509__commons-w3840.jpg` | `File:The School of Athens by Raffaello Sanzio da Urbino.jpg` (original 17402×12132, 207 MB) | Public domain | 3840×2677 (miniatura generada por Commons; se pidió 6000 px y el servidor entregó 3840) | `b32e3fd8873732a2d2ac938aca682e67a00340b0638977b79eb63bf280e516ab` |

Nota: la primera descarga de `baco` devolvió una página de error de Wikimedia (3 KB); el reintento funcionó.

## Copias de trabajo (`work/`)

Las que usan las tres condiciones. Lado mayor limitado a 4500 px (Lanczos, JPEG calidad 95, sin submuestreo de croma);
`atenas` y `julio2` ya eran más chicas y son copia exacta del archivo de arriba.

| Caso | Tamaño | SHA-256 |
|---|---|---|
| `prato` | 3514×4500 | `077d529b71c3e112e2f1d90fae209fbf97f0af3ce66a457c01b832a747a80ba3` |
| `arnolfini` | 3289×4500 | `27caaf7b3b802cb20466a51a560e24ef46cd34c2068786c5ac5192f333a42c7e` |
| `baco` | 4500×4072 | `dc0e19a829467aba8f0c3887cc0e83744dc0d623493d681dbc4ee24725e0db10` |
| `atenas` | 3840×2677 | `b32e3fd8873732a2d2ac938aca682e67a00340b0638977b79eb63bf280e516ab` |
| `julio2` | 3111×4227 | `2bad12ee07017bd8ca74853586751b8bbdd4cd739124de4935e036475d5b73a2` |

## Segunda tanda (2026-11-17), para el museo

No forman parte del experimento: se intervienen con el método combinado de máscara automática (`scripts/auto_hybrid.py`).
La descarga de los archivos originales dio error 429 (límite de pedidos de Wikimedia) en todos los intentos, así que se bajaron las miniaturas que genera Commons: 3840 px de ancho donde el original lo permite y 1920 px en las tres más chicas.

| Caso | Archivo local | Archivo en Commons | Licencia declarada | Tamaño bajado | SHA-256 | Copia de trabajo |
|---|---|---|---|---|---|---|
| `armino` | `armino__leonardo-1490__commons-thumb.jpg` | `File:The Lady with an Ermine.jpg` (original 3488×4560) | Public domain | 1920×2510 | `0f035d70583961710df5b6f5f2efe774a84e82b0340f8c4ce99280ddbc5e8c16` | 1920×2510 |
| `gioconda` | `gioconda__leonardo-1503__commons-thumb.jpg` | `File:Mona Lisa.jpg` (original 2835×4289) | Public domain | 1920×2905 | `7dcafd61444d9f0c8d263aab3a8306e1db1b19ec1c980c7eb19a01a3e6fffe52` | 1920×2905 |
| `castiglione` | `castiglione__rafael-1515__commons-thumb.jpg` | `File:Baldassare Castiglione, by Raffaello Sanzio, from C2RMF retouchedFXD.jpg` (original 4096×5095) | Public domain | 3840×4777 | `b5b9887a71bbc5228ad53f3a226633e693508505d690c8695c831cb0d188c06b` | 3617×4500 |
| `eleonora` | `eleonora__bronzino-1545__commons-thumb.jpg` | `File:Bronzino - Eleonora di Toledo col figlio Giovanni - Google Art Project.jpg` (original 2553×3098) | Public domain | 1920×2330 | `0e919129d9f71fb15472b53666a78c4bc356426de8e61955e5cc7d51b3531416` | 1920×2330 |
| `embajadores` | `embajadores__holbein-1533__commons-thumb.jpg` | `File:Holbein-ambassadorsFXD.jpg` (original 4215×4226) | Public domain | 3840×3850 | `9d4ecdde77f31c60f70e29cccdfb6a01a4e01b20ecdb1f257c26752965615e6b` | 3840×3850 |
| `enrique8` | `enrique8__taller-holbein-1540__commons-thumb.jpg` | `File:After Hans Holbein the Younger - Portrait of Henry VIII - Google Art Project.jpg` (original 2040×3588), bajado el 2026-11-18 | Public domain | 1920×3377 | `a91c9a17bd6e8f4d103a8bd8ff8e35125ba6b1010199c7aaa511fb56de5b1a89` |
