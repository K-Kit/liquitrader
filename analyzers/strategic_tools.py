import os
import time
import base64
import json
import sys

import requests

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


server_pub_der_obfusc = 'MzUtNDAtMzAxMS0yMDYtMS03MTcxLTMtNzMtMi05My02LTgwLTU2Mi0yLTktMy03Nzk0LTYwLTQ4LTk2LTYyNTgtNTgtMTkxOTQtMzgtMjg1LTUtMi0xNTgxNjIyMDg3MTc5NS00NDAtOS05NjYxLTE5Ni0xLTM3LTYtNy0yLTI1LTIwMS05LTI3ODIzMi01LTcxNDI0MS00LTMtMi00NzUtMS0yNS0xLTQyNS03Ny0zLTEtNzAwLTU2NjAtMTktODktNjg1LTMtMi0zLTg1LTYyLTI5NjMyODItNC00LTEwLTI4NTg5MTQ4NS02zNTk1NjgzLTk4LTQtNDk3NC04NDQtNDI3NS0zMzU3LTMtMi0yLTczMC05OS05LTc2Mi05LTktNjgtMy05LTgtODktODgtMjE4LTEtNzctNzAxLTY2NDMtOC03My00MTE1OC01Ni00ODc0NjQtOTU3MjktMy04LTMtNjktOTUtNDItNDUwLTU3LTgyLTk5OS02NTYtNTc0OTY4LTMxNDU5My01MTAtNDQzNDE5MzMyLTMtODYtNDktNy02LTYtNjktNzEtOTQtMS0zLTQxMy0yODU2Mi05MDczLTctMy0xMi0xMDAtOC0yLTU0Mzk4LTY0NjQwLTE4NDgwNjgtMzEyMDU0MDc0LTQtNC0xLTUtMS00MTUtODItNS03ODU5OS02LTQyMzg2OS0zLTMwMzUtNTYtOS05LTQtNjc3LTgtNi0yOS0zMy0zLTUzLTExLTEtMTgyODE5MDctNS02LTUtNDAzLTgtMTMzLTktOS0zNC03MS0yMS0yMzkyLTYtODMtMi02LTMtNC0xLTQtMy0xLTIwLTctNy0yOC0xLTc0Ny00LTMyLTEtOC00OS02LTMwNC02NC00OS00OC05NC00LTQ4NTk3LTMtOC00LTQ1LTctMi02LTItMTU2LTQtNi04LTE3LTg5LTYtODE2LTM1MjAtNi05My02Ny0yNC04MzctNS03MDEtODMtMS02MzkxOTk4NC00LTctNjgtNTAtNDctNy0zMy03ODAzLTg5Ny05LTk4OC05NzU2LTktMi02NjEyLTQtMi03LTM2Mi01ODc3LTItNjYtNzEyMTAtNS03Ny0xLTQtOTEtNy04LTItNjYxLTktMi0yNjgtOC03LTIzLTgzMTctMy05NTE5LTgwLTYtNC0xOC02LTU2MS04MC00LTk4LTEwNzYtMS0yNS05Ny00NjU5NC01OC04LTUtMy01Mzk1OC0yLTE5MS04LTQ5LTItNS04NS04LTEzMzEtMjQzMjEtNy05Mi01NDg5LTMwLTEtOTYtMi05LTg0LTctNS03MC0zNC01LTQyLTgtOTU3NjEwNC0xMzctNDQtNjgtNzEyNC05LTI0MS0yMDYtMy03NC00LTYtMy04MC0yOC0yLTYtOTQxLTctODAyMzYtNDIzLTEwMS0yLTctNTMzMy01Ny05Ni01LTUtNTU5OC01NzYzN340Ui5JLkIySi9qN0AqTzhDLmA0aSh0K2AxZjdrLz4uMjjCgDUqMT45ODdLM0o5QTpAOlA6Ry5JL1k2My9ANlUzTzNEMUs4aDhUNj81QShIN0syQDrCgDBfOGgqYC9xL0syKi9eOUM0UyxlMmozMzJyLkotSzZBL3swNDM+KlYuaipTMWo3ODFROlo6XTlHLnYuPjZsM2I6PjRwOUgtYjBFL3I2XTpbNVY2czZNNkc5Vig6LVU6VDU8NX0tZzhQL1E2fS5KL2o0WijCgChvN0UoKCtxLkYpPzpbOVgyNzBdOHAxMitsNUwpcDRCMmc2VCw1LT44TjdRKH84ZzpsKUkrdih4LVYtUzFyOGszPzrCgytvNy84VDpgOVUyTTZ/NDEyWS1vNE8yWDRXMzEpPS1uKlIrXjpOMjk1RC5kMksvdTZeM1gxfTRqLlYzZjExKXIsTTRCOW41WzVpMF01fjE7OXcyRzFuNTk4ay0nMEcwXjJfKUwsMTl9OnkrMDM4OXM6Ui55NDwsXihZLWY4aSkuLz8uRi4tNDQyRTBxM1cyfjFcLEcsMTF9KTY0MyhcLkcqLC9kL0Q6UCtLNG4rdS1VLW4wNDFjKlc5UCo6OD4ueDBxLTQrRjE6K1gtPi08KGstdTlpOlsuMC1FNkcvQi9XNj8tQylgOGA6QylqNzA2cDFlKEsraC82KTY4LSozMiM0dys6OlI6Pzl3LTErPSxXLTIqMzQrOWw0UDrCgChjOU8ofzY1KG8rUTJ6LWkqdDdpLEE4Mi8qN0cybDJPLGo4YS5rMl4pZis+MmkvNzdLKSsvWik0Mn8uXzY6OlwxTi1sOXEsazJBMUsoVjBMOHgwRDZAODM3dzpZLHApVS5GNHk2QC9wOiwpSzozLCc2PTA6NHEvVDQzMnModyxnOXYuZTBxN2YocDVpLC8xRzVSLTkpRzZzNzYxVTBGODA1OzltMjs1LS9HMkIxOi4kNUcrbSk0L3IvOyhJMmgpcTNbN3EzVTB0MmgqdDR6NEE4bjdELD82SjlMOEc0SQ'

liqui_priv_der_obfusc = 'LTEtNy0xNS01Ni0xLTUtNjItOS02LTQtOS0xNy01LTUtNTItOC05LTMwLTkwMjI4LTM0OC03MS05MC0zOTIyLTUtNS05LTI4ODczNjUtNS04NDEtMy04OTgtODY5LTUwNDU4LTY5MDktNy0xLTk4LTgxLTctNi04LTUtOTUtMi03LTk3LTg1LTU2MTUtNjEyLTYwLTIwOS01LTUtOTUyLTUtOC0xLTQtOS0yLTgwLTMxLTk0MjIwNi01OS0yLTItODQtMTUzLTE2NzU0LTUtNS05NDIxOTUtNy05MTAxMTY0LTk1LTEzLTY0LTk2yLTQtOTQyMS0yMS0yLTg4LTEtMy05OC04OTY3LTk4LTkyOTU4LTMyMS05LTk1LTYtNjQzNTYtNC01Ny02Ni0xNi03MS0yNzI4LTcyODkyLTctMjMxNC02My0xLTcxNS02LTQtNjI3LTM5MjU1MjQtMi05Ny01LTg1MzUtOTQwLTY0MDU0MTgtMi00Ni0yLTEtNjEtOS05NDMtNTgtMy0zNS03LTc3NDM3NTgwLTYtNjIxLTk2MjcxLTM2NjctNjQwLTkzLTEtNC02MTAtNy02NjktNjgtNC01LTgwLTYyMy00LTctNzAtNTM5LTItMjEtNjItMTMtMy0zMi05Nzg5LTctNTQxOC0yNzgtNy03NzYxMC0xMS05LTItNjctNy00LTgtNDgwLTE1LTEtOTA0NS0yOS03NzIzNjk1LTYtNzctOC01LTk1NC01ODY3Ni01NTItNDI4Ny05MDEtMTk3Ni00LTQzNjE5LTI4LTcyLTQtMi05LTM4LTgwLTQ0LTc0ODczOTQtNy01LTUtNy0xMy01OTcwNjgtOC0zNTMtNy03MjAwOC0xNDUtMi03MS00NzI1NjUxLTEtOTI5LTM0OTcyMy05Ni0zNS0zLTktMjkzLTQyNTYtMi00LTcwOS05LTQtNi05LTQtMzc5LTctMzYtNTU5LTItNzU4LTctMzMtNS0zLTY3MS05OS0xLTctMTQ4OS03LTI4Ny0zNDktMS03ODQtMjUtMjAtNy04NjUzMS02MzktNTc5MTItMTEtOTktOTQtMy03ODgwLTU0LTQ0MTUtOTAwMTA1Ni01LTMtMS0yLTYyODMxLTg0MS05Ni01LTEwNS01OS04NTk1MTg4LTItNTMtNS00Mi00ODc4LTgtMy03LTctNzUwLTktMjYtMS04LTQtODctOTY2LTktNzg1MTU1MS04NzczMDAtNDIxMjMtOTczODU3NjItNS0zMS0yMTI2NjU0LTMtMS00LTUtODItMzQ2LTYyMTQtOC04MzgxLTQyLTk2NS0xNC01ODktNzg1MjctNS0xMzktNS05Ni04LTM4LTI3ODAtNjE1LTQtNy02My03LTUtMTMtMzIzLTUtNjU2LTctNDUxNy0xLTQ3My04MjAtMTEtNi04LTItODgtMzEzNi01NzktMS00LTktNS04LTktNzItNjItMS00NS01LTItNy05MjU1Ny00LTMwMC00LTctMjY5LTk2MzIxLTYtMzEtOTkyLTU3LTY5MjMtMy0zODAtMS03MS04LTc5MS0yLTEwOC0yODcwNTA0Ni01LTItOTktNi0zLTUtOTAtMzctMy02MTU4LTItNy01LTUtNzc0NS05LTctMjctMzctNTI2Ny0zLTU2MDMtMjgtNS0zNi0xLTMzNzItOS05Ni03LTUtNDU3NzAtNi01LTQtMi05LTctNjg5MC01LTMxLTEtMjYtMy04LTI4LTY2ODItMjEzMi0yLTgtNS04ODE4NTkzMi02MTQxMzgtNzYtNy0zMTk1LTcwNTQtNTQtNi03LTk0NC01LTgtMy05LTE0LTQ1NjUtMS00LTQtMS05LTQ4LTM3MC02MzAtNS01LTQwLTYtOS02LTktMi0xMjAtNy00LTMwLTItNi02NDAtNC03LTYtOS04LTQtOC02OS02LTYyOS04MC00LTQ3My0xLTczMjkzLTYwODAtMi01LTM2LTM1MS0zLTQ2NDItNzYtOS03LTQyODUtNDItOC05LTctMjAtMi04MS04NDMwMC04LTg5Mi03MDA1NTAzODc0My02LTYyLTctNC05LTE3NjgtODMtOC02LTgtOC04LTk1LTEwLTc0NC04LTQzMy02LTMtMi01LTEtMzY1LTc5LTQtMzI3MDUtMzcwNjgtNTY0LTU2ODU1LTgxLTc4LTUtMzMtNy03LTgzMy03LTYwMy04LTktOC0yLTMwNS04LTYtMS0xLTkzLTgzMS02LTU4MC0zNS0yLTEtNi02LTctNS01OS03LTYtNTQ1LTQtNi02MS0zLTMtOC05LTktMy02LTItNy01OTktOTYxNC04NjgtNS0xLTgwMi0zNzctOTItMzYtMi04MS02NjItMzQxLTIwMDUtOTEtOS0zNTAtMS02LTg3LTQ0Ny0zMi0yMDctMS0yMDktODYtMy0yMDQtNzgxLTQtNC01LTQxNi0xLTYtNDMtNTExODExLTM2LTU3LTkzLTIzLTU4LTEtMS02LTMwLTgxLTQzLTg5LTkyNzAtMy03LTEwNC0yNC04LTcxLTQtMjEtMS0yMDcwNjYtMjAwLTUtNi03MzctOC05MjIzNDMtNDEzMS0yMTktOS0xLTU3LTY3LTYwNy0zOC0zLTgtMTYtODg0LTE3NC00My0zLTUwLTk5NC02LTY4LTgwLTktODA2Mi0xNy02LTQxLTYyLTI5LTMtNS01MDk0LTktNC05Ni0xNzQ5LTYtMjIyLTU0LTctNC04LTQxNS0yMi03LTQtNC0xLTIxLTU0Ni04NzA2NzctNjAtMTAzNi0xOTctMi00LTMxOTE4My01LTQtMjItNzktNy01LTItNy0zNC04OC00LTgzNzE0MjItMzgtMy0zNzctODItNzIzMTU0LTMtNy0xLTMzLTUtMy0yLTctOS03LTItOC04MDYtMy04LTY5My05NTEtODE3LTUtNDY4LTEzLTcyLTgtMTctOC05LTgtMzgtOTk1LTItNy00MzcyLTY5LTIxLTUzNS03LTUtNC02NC0xNDctNS02Ni0xLTUtNjctMS03Njc3LTgxLTg0MDM2NDAtMjkxOTIwLTQtNC01MzQ4OTQtMTg5MTgtMS00LTQtNjYtNTItNy0xLTE2NDAtMS05LTUtNi0xLTItNjktOS0xOC01NjQ4LTMtMjktNC00LTYtMS00NjQtOC0yMDY2NC04LTUtMy0yMjI0My0xLTgyLTgyMjYtNjA4LTgtMzMtMTA1LTUtNTE2MS03LTYtOC03LTktNDcxNi05My00Ny03LTQtNC05MTQ2NC0zOC05OS04LTEtNDUyMS0xOS01MDg0LTExMzA3LTctNTU4LTU5MDYtOC0zNS0yLTgtOS0zMDA3MC01LTUtOS04My05MS0zOS00Ni00LTktMy00LTE5MDItODk2LTk2Nzc1LTc5LTUtNDc1NDM5MzUtNTg1OS0xMTAtNS05MjAxOC02LTUxMy00MTktMTk0LTMtMy05NzAtODEtMjktNi04NTktNy0yMS03LTktNTQwMDcxODEtMS00LTIyLTkwMTQtMjktNi00LTgtNy01NS03MTItNi0zLTUtMzgtOC04LTMwNC00LTUtNi03LTQtNS01MzItMzM3LTEzLTYxLTItOS00LTYtMTktNi0yOS04NS04LTQyMTQtMS0yLTUtMS00NC0xLTYtOS04LTMtNy0zLTYtNS00LTQtMy04LTctNi03MC02LTItMi00MS0zMDE2LTktNC02LTU0Ny02NDM1LTE2LTc5MTgtMi0xLTc4MC0xNzQtMy00MjAwMDg1ODYxNy01LTItMjAyMDg0OTAtNS03LTM2LTktNzcwOC02NTg5LTUyMjY4LTIwLTQ5NDctNzktNy0yMi01NC04NDI2LTc1LTYyNjA0LTQ4NjcxLTkyMC01LTc0LTUtOS03LTU4MjY3LTQ5LTctOTA4NS00MzMtNjQwNjA0LTQ4LTktNi04MzgtNS05LTYtNS0xLTc2LTktMTYzLTQtMTQtNDcxLTM2MC02LTI0NDkzNS0xLTgtNDgtMy00MDktNjU4ODMtMS04LTEtOS00NzcyNC0zNjYtNDI5LTMtNS02MzctOS0yLTYzLTktMjctNC02NTYtNzIyMy00LTk3NC02MDI3LTQwLTUtNzA5LTUwLTQyLTc3LTM1NzM5ODk5LTY1LTMxLTYwLTg4ODE1MTAzLTc4LTMtMy05LTQtMi0xNTYxMi0xLTY2MjA2LTc0Ny05Ni02ODgtNTE2NC0yOC05OTQtNDktNi02Ny0xLTUtNjQtODEtODgtMjg2NTYxNjAzNi03LTcwLTgtMy01LTEtNy02LTc5MjctNy05LTc5Mi0zMi0yMi05LTYtOTg2LTItNC01MTEtMzAwOTgtMjUtNi02LTYzLTUtODEtODY1LTQ4LTctMTktMzYtNi00Ny0zLTQ1LTUtMi03OC01LTIxLTMtMS04LTQtNTMwLTUtNy04Mi00LTQyLTc4NzYtMy0zLTIzMTctNC02OC0xLTYtOTgxNy04Ni00NTAzLTctODItNzQtMy0yLTEtOC02LTktMjkyMDgtMTgtOTEtOS03LTQtOTUtNy05LTE4OC0zLTEtOTctMTYtNzktNS05LTktNC0yLTEzLTYwNjUtOC02MjYtMi00LTM1Ni01Mi0xOTM0LTktMzItNy03LTctOC0yLTg4LTE5LTE5LTY5OC02ODcxNC02NDIyLTktMjMwMTgtNDM0LTctNTYtOS04ODEwLTktMi02LTk3OC01LTctOTU0MS0yMi04LTk1LTQ1MjkzLTEtMi0xMC05LTEtNjE3MS05LTE3OS05OTkwLTY1LTQtNDQ0MC03LTg0ODIyLTEyMi00LTYtNzg3MjIzLTQ1LTEzOC03LTktNDMtMi05MS04NDM2MTUwLTYtNC0yLTcyMC05ODYxMzgtOTMtNTQtOC02MzI4OC0zOS0yODYtMi0yNTc0NC01LTk1OC00LTUwLTUtOS05LTMtNzYtNTkwNjMtMy05LTktNTMtMS0xODEtMS05LTctOS00Mjc1LTM1Ni03Ni00LTEtNzY4Mi0xLTc3LTEtODI1LTU2MS0zMy01Mi05Ny05LTkyLTctOS0xNjktNzQxNTItMTItNTMxMC02LTUtMS00LTUtODctOTYxODcxNTEtNS04MzAtODkwLTktNC02LTkzLTU5MDYtNzI0Mi03LTk1ODItOTQzMDMyLTgtNS0yLTQtNS0xLTgtMzYtMy0yLTMzMTgzNzgxLTEtOS0zNDEtNTU3My0yLTM5MDg5Ni0zLTMwLTktMi01MDItMzEtNC0yMjM1Ni02MzgtMy04LTQ4LTgxOC01LTY3ODktNjk3LTg3LTcyLTQ2NS05LTgtNi03MjI4LTg0Ny03LTktMi01Mzg5OC05LTgtOC02NTEtNy0xLTUtOS02MzgtOTUxLTgtNzktNzUtMy0zLTczNC05OS01LTItOTczLTItNC0xMi04LTU4MC0zNy05NzMtNjM2Mzg4LTItNDQ0NjEtMy05MDA4NTg1LTktODgzMi05MDc0LTktNTctNDktOS02LTMyLTctNDctMy04Ny03LTcwLTMtNTMtMzA0LTctNC04MTctMTIyNjctMjQ0NC04LTE3LTEzNC05MDg2LTEtMTgyLTE0LTMtNy04LTktMjEtOS0zMi05LTE5LTUtNjItMzItNy03OTE4ODI1LTk0OTAtNy01LTM1LTI3MzMxMy04MS0xMDgtOC0yNC05LTM1LTktOS00LTU4LTE5LTEtNjMtNi02My0yLTUtMy04LTIyLTYtMzgtODU1MTQ1Mi0xLTk3LTktMS0xMjExMTUtNjYtOTYtODQtMS0zLTEtMjI1LTY4LTM2NzYxMTAtNDYtMTE0LTU2LTktNTctOS00OC02MTY1LTgtNTUwNjAyLTk2MC00LTQtMi00NjM3NTItOTYtODUtMy00NS0yLTc4NS01NC0zMjMtNy01NTY2LTUtODg3LTQzNS02LTktNy05NjItNzEwLTEtNTQ3LTk1MTYtNS03NzU0My05MjY4NS02NjA0LTMtOS05LTctMS04LTUtMy04Mi0yNTg2My0yMy04LTI5OS00LTktOTYtMjktOTYtOTItNy03NDMtNS0zLTgtODA4LTgtODU5OC0yLTgtOC0xOS05ODg2LTItNi0yLTUtNH4wRjFOLEswcStDKEMtOTBILD8sQylFLkIoZzNtOW41cCpsKGkuUDM7LHIoLjlKOEQ3Viw9NUcvOTpbKUk6PTFPNmErwoAycCpSKHEpQiphKUApRi9oKFApRyxHMlYrRDNcMTQxaiwsKDczYSlELU4vWzFFMlo1bDRrN186Ly9sNWs2SjA+ODo1XywsNUcySzZeKEQxeDJ4NWs2ZDQ9NW0zdShvM3EvUC89OWovXTlmOmk4PjlRM002YC54MjooSSwqNU02Zy1zOEY3cDdiMkk4bTkvM3g6ZSpDNHc1MzROKkw2Pi1LM28uXzNpNlI1ZihVLEM2cTZmNWcrWzFMNTM5Yi07L3crWignNU4sPi4oNloqNzUyOVA5NCtMM2coODNYMmw3WzhqNXIocTB1K3ExbStqOnM5US1lMW8zUy1uKmcsNjprLywsUzAuLjUzPDhOOi8sVjJAL2s5ZSpYNzoxSjJlL0U4Zi0xLXwxdDZCKFM1by9WKk4zSzdvNlEqeSlzKG01aDl+OGcsXTNhM184ZjFHMMKCOF8tLDRYMjovTSpTLWcoTTk7MUk1TDVqOEg6UCpTLEAwNyxdODA3OilWNnEqczRZMTgwZTY1KnstczM9N1UyOChHOmg1PzhxNGw3RTZsKFg6OS1vNnYvaCpjOiktVCgrLjw6Wy48LFY6KStnOWsuNSxmK3wyUTo3KmI1woI6Uy9/OGA1WTAxOXsvXS9XKkk3fDRVK0Q6RDg4MlUwVShtKHAuUDk/MjQ1LjVpNjgxQzJSNnIsYDBBK005WDIpNUcodywwMVcsOCl6OmsyfDlALEYsTzNLOT85Zy5HKnA2SShgN3YpLCnCgCh1N0UqTTZYNn8yXDh8NE0xdTNCMzkoVjQ6Nk03LSxLMlQyeDdNNnIuUC10KVUudjdMM001bSlOOTgteyhYNkM1LTltKlQ2bzg+MHA6SyhyKXI5dThQMSsydi07K1oqKzBvLnI0YStMN2EtfjJ3MFE4Ril3MVEyMClkKcKALkI0bSxUOkEuOCw9KDw0YTNELUYsSStwM1w2YC1CMTAtYS9nOlA3NjNHKzIyLTpZLFQrwoMzOC42OWUwKDJPKmsyZzB2OUk5czF6MWc3Xy9uOi0uZSgvLmEuSzJtOVIqVCw8OHk2SipVOVA4bTNVOC4sUDFdL1gsYzdHLlk4RShFN0gsQzY3OEgrZS01KGcrMzp1LFAyeS9/LisvUys6OWUvQzRJL2csOTlLOV86WjNpMjQzXTldN0EuUzppKmI2ZSx+KzAoVDUzKUAoWTVSNl02Ty1qMGYtey5fMWE0NCxjLTMrcStPLzIzdSo9LnovVCtcMUIqUSgpLUcrUCtGM3ApTy1hODowTzQ5OlYrZzl1Ly8uTC5tMlItSzU0Kn0oOy13OT0tTCkrKkYxbyloKTU0WTFHKXEzPDE4NjkxTDnCgTU7K3QzPS1jMGo3VSl8KUopTikuNkcxcDVuKUk0cytRLzAwRjdRKmAtSTNcMU8uTDFqOXE3cyx+OX42MDIrOUwuVSpQKVs0Pys3NFkoRy91MXwpRDBPKFgpdzJMLE0xVzZnMEIrQiwtOmgrLjVJLV4rei51KUQoait1Km86XSh4MjYpXzkmMCsxbS59OGAzcjc0KXIrXjNINXkvZTFGKHIoTzZOME0pdy1vOFIzYDHCgTBYMTwpSS40MU4qOjJnLWktNDdWK140cjIyOXUyKDctOD80VDQqOUcwMC43KXItUCl9KEc4Wi5vMG01UTZcKnItajJML2E4RTdOL3kxXSxsNF8pWDN6NDc0RjJbMm8yXihLLT8rPCswOGo5YylEN0Q5NjB7NWM0TixSKF81bStWKTcoZTFpM2E4Mi02K1AvfC5sLG06XSgvKD8wPjU9K0UzaCxZKkIpUzJ1LzcqYS1KL3MsTzdOOE83TThyMVQxNjd2OlgvRy5DOmg5VCxAL0wqdCpEL1EucClVLUo0fzJOM0QufS4oOXUpZSp8NHk2VC4qMGk0QS5QKj8qQilRMUkuKyt7NF82OSlsOD8tWjlANDAzKzBqKWUpNTliOnQvXy1kODorUS9TLDQ2Qiw+K2kwVDhyK8KAMCYrUjBLNzs4bjIxNVI0PzVkL1UyYDNxLUAsVDVqOjcwSjpSO3ItcitTLFcqdDBaNW0wKSxjMDcrTChkOSw4SDlELzgtcytGLW41QC9zN1k1XCxJL2ozZjRqKVcpQzNeK2k5Pi5ZMHA2cixzNzgqMClGKC44ajdaND04Qi1zKEU1MTVOOSs6XDBQNm8yczpHMVY1NzJaMXsqSjZ1LMKCMXopMTZEKUcuWTFQMS0sQilHKGIuWS1fLWIuLjB8MUMpfDdcNz04Uio/LFE4fzV4OlE2Tjl3OlAyVywsMysyVitKMjotZTpQOk8uPyhuMUkyQjpBKUc6SS9PKmQsfjFjOGw5WTBnLzcocDJoLzorQiljLHwqNzNzLksuWSlMLnI1MCxSKlIscTRHLlE4ZzRrMjMoKytrOkAvTClnKUIzZTUvLzEwQTU2Ky0pdyp0K1EtLS5eKjwqUCtlLz0yaTFuNzgtXSxcOGE1VzdAN2A6WzloMHA5djBxNlctLTFvMXk2Xzd5OHEvLzFSMl81WDE0KlE3ZCp/MWIrdjlVLHAzOjlfMUk6TThfOmYvaCw3KWYzeSpfK3o3cjUuOXU4ayhpMWgrXiw9KjQ5aDdeLWIqJjF9NlM0bytyMWoxWS1wKDIpSTkrKGgscipXKEo3ay1gNWI4ay5UMXIvVTVQNEgwTS05LmUxTCtsOV40TykvKGM4VDRwLjE3TDM6LksrcTgwL3M0US87LT02ayoxM3QtazhMK3kzby0wLCwxTSxRLU0qSS5sOEg6WjpTK20uVitOKVA5cTZ5MWwqUy5pKD0vaTZRMmMwZjdQMVwqUDhcNy85VSxyN04veChjNUE6UCtOMFUrTClEKVUvcDdWN243SzRSKlwxMC48MFErPTpLOEooKDp5Lm8vWShkKF03bC1VMmUuQjE9OU02bitDNF8pVik9Nj45OjDCgy5WK2U4dC16LEYqTixzMmgwTy0tNDAsZil0LUEzcDldN2wuUTR0ODErODBgKH0yOik+LUwxUSpRMy01Si9UKS4oNDoxMXEwSih1KGItODY8KDI6XS5OKGgwTCp8LGMobi9YNHExcTZkKzI3cS1DNlgsczBhNGwoRDNnK0QpTSk9MH0waytzOW45WDI9K20zdShuNFAyMy10NT4sbShmOXsxbC9KKFM5SCpmNnAyTjNJKEgtXDN0NEMvYzFlMEAyeDJmMHU6MDo+MV82Uy09NUEqZzVPM0MwRDNNK005UTNJNGo2aTR5KmwtUS9EMic1NjdXNkwrcC9cM2koXzd7NG8oZCx3KUg0UjlOLkowwoE3Yi9NODk1PihJOWUsOSw9KGgqSy12McKANHAoKSw3MFE5MjBqKl0tWThaLks3Kzc+MFE3OzNrKj0wOjM3LGAyQzRvM2Y4cChDKm8xNTo7NXI2ZDBKLDoybStzMF0sajhLN0Y5dzJ+MnEpbzEuOjIoMCtZNGI6TjcxM0czQSg9OXgoPDRYNEwpTC9KLEopVjdHLy40cDlXOFQyQygwNTEtfDhdL3c6bTpvN2AuQyhPLGczMzIzL3o0TjcqNEsuPy07KVk5QSt1OcKAK1g4TjgwM2A3NygjK3IzODkqNVAqbS9qNHM6bCg8KVA2eipkLEsrWjllNnMpXDo7NmQuKjRIKHAsQyhYNF8tRjNMLGkxdThCOFErMzdGOW8vVTVFNzAuOzFROTA5aShbOVszSzFANW4seC10KCsuaio/ODQpSypdMVcsUy5GNWUtRzJaMHwzcjhoNW81TjBMMHA1QzFWN1gwdjNYNWkqLShjMi4uTyh5OiYrUy5wKjw6cDlRM0ooRTowKnAuWS9NNDoyRil5MGY5Yi9lKEw2RChrLEEwVzBNNEoraC9JLlovUit2OWY2NDJyNkUwKDguMEczajNJNmE3PjdgNTQubi9bNk45QzdoN3QyTS1fMFU1MDdRLG8oSzlTMkw2WSxVMWkxMihqMXItQS1INFw2dyg7KTcuVTZgKj02cjUtNFkqSjY4Nz8pTjhvNHkrOio/N0kqMDE1LFQ4TzZ5N0IqeTZpNEUzOzlpK2wxZS5iKD8wcSw+KXsvXzlaNHg0QC9KOiwoRzdGOmE3UTNtKnw0SC5MKXA5RSl+OlcvRCl0OnA5bzc1K2UtOQ'


# ---
# Generate private and public keys
# These will eventually be set in stone

def rld(string):
    decoded = ''

    for run_length_pos in range(0, len(string), 2):
        decoded += string[run_length_pos + 1] * int(string[run_length_pos])

    return decoded


def unshift(string):
    split = string.find('~')
    key, shifted = string[:split], string[split + 1:]
    shift_table = []

    next_neg = False
    for sh in key:
        if sh == '-':
            next_neg = True
            continue

        shift_table.append(int(sh) * -1 if next_neg else int(sh))
        next_neg = False

    unshifted = ''
    for ch, shift_amt in zip(shifted, shift_table):
        unshifted += chr(ord(ch) - shift_amt)

    return unshifted


def load_private_key():
    rl_decoded = base64.b64decode(f'{liqui_priv_der_obfusc[:315]}{liqui_priv_der_obfusc[316:]}{"=" * int(liqui_priv_der_obfusc[315])}').decode('utf-8')
    rl_decoded_unshifted = unshift(rl_decoded)
    rl_decoded = rld(rl_decoded_unshifted).encode()
    rl_decoded = base64.b64decode(rl_decoded)

    return serialization.load_pem_private_key(
               serialization.load_der_private_key(rl_decoded, None, default_backend()).private_bytes(
                   encoding=serialization.Encoding.PEM,
                   encryption_algorithm=serialization.NoEncryption(),
                   format=serialization.PrivateFormat.TraditionalOpenSSL
               ),
               None,
               default_backend()
    )


def load_server_public_key():
    # The 315th character is manually entered; it is the number of '=' stripped from the end of the base64
    rl_decoded = base64.b64decode(f'{server_pub_der_obfusc[:315]}{server_pub_der_obfusc[316:]}{"=" * int(server_pub_der_obfusc[315])}').decode('utf-8')
    rl_decoded_unshifted = unshift(rl_decoded)
    rl_decoded = rld(rl_decoded_unshifted).encode()
    rl_decoded = base64.b64decode(rl_decoded)

    return serialization.load_pem_public_key(
        serialization.load_der_public_key(rl_decoded, default_backend()).public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1
        ),
        default_backend()
    )

# =======================================================
# SEND SIDE

def generation(license_key, api_key):
    # Generate a random message (bytes)
    random_data = os.urandom(8)

    license_bytes = bytes(license_key, encoding="utf-8")
    api_key_bytes = bytes(api_key, encoding="utf-8")

    payload = b' '.join((bytes(str(time.time()), encoding="utf-8"), license_bytes, api_key_bytes, random_data))

    try:
        encrypted_payload = load_server_public_key().encrypt(
            payload,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )

    except Exception as ex:
        print("Verification error (1)")
        return None

    encrypted_payload = str(base64.b64encode(encrypted_payload), encoding='utf-8')

    try:
        payload_signature = load_private_key().sign(
            payload,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

    except Exception as ex:
        print("Verification error (2)")
        return None

    payload_signature = str(base64.b64encode(payload_signature), encoding='utf-8')

    return str(base64.b64encode(random_data), encoding='utf-8'), payload_signature + ' ' + encrypted_payload


# -----
# RECIEVE SIDE
# -----
def verification(data):
    try:
        data_parts = data.split(' ')
        signature = base64.b64decode(data_parts[0])
        encrypted_verifier_data = base64.b64decode(data_parts[1])

    except Exception as ex:
        print("Verification error (3)")
        sys.exit(0)

    try:
        decrypted_verifier_data = load_private_key().decrypt(
            encrypted_verifier_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )

    except Exception as ex:
        print("Verification error (4)")
        sys.exit(0)

    try:
        decrypted_data_split_index = decrypted_verifier_data.find(b" ")
        timestamp = str(decrypted_verifier_data[:decrypted_data_split_index], encoding="utf-8")

    except Exception as ex:
        print("Verification error (5)")
        sys.exit(0)

    time_elapsed = time.time() - float(timestamp)
    if time_elapsed > 30.0:
        print("Verification timed out")
        sys.exit(0)

    try:
        load_server_public_key().verify(
            signature,
            decrypted_verifier_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

    except Exception as ex:
        print("Verification error (6)")
        sys.exit(0)

    data = decrypted_verifier_data[decrypted_data_split_index + 1:]
    return str(data)[2:-1]


def verify(license_key, api_key):
    data, generated_verifier_data = generation(license_key, api_key)

    counter = 1
    while True:
        try:
            validation_request = requests.get("https://bearpuncher-auth.azurewebsites.net/api/v1/user-license/validate",
                                              headers={
                                                  'user-agent': 'liquitrader/2.0.0',
                                                  'auth_key': 'aAgTQITwDdEv1xobEwQmhvjPZ4W/Jl26HWc2pnNwXNEZYpd4VEouEQ==',
                                                  'data': generated_verifier_data
                                              },
                                              timeout=5)
            break

        except requests.exceptions.ReadTimeout:
            print(str(counter), end='')
            counter += 1

        if counter >= 5:
            print('Failed to connect to LiquiTrader license server. Check your network connection.\n')
            sys.exit(0)

    if counter > 1:
        print()

    try:
        server_response = validation_request.json()

        if type(server_response) == str:
            server_response = json.loads(server_response)

    except json.decoder.JSONDecodeError:
        if b'Web App - Unavailable' in validation_request.content:
            print('You are either being rate limited or something went wrong with the license server.')
            print('If have not received a message about being rate limited, please contact support;')
            print('otherwise, your 10 minutes is not yet up.')

        return

    received_verifier_data = server_response.get('verifier_data', None)
    license_time_remaining = server_response.get('expires_in', None)

    if received_verifier_data is None or license_time_remaining is None:
        error = server_response.get('error', None)

        if error == 'Invalid request (8)':
            print('Verification error (7)')
        else:
            print(f'Verification error ({"8" if error is None else error})')

        return None

    received_data = verification(received_verifier_data)

    if received_data is not None:
        if data != received_data:
            print('Verification error (A plea from the devs: we\'ve poured our souls into LiquiTrader;'
                  'please stop trying to crack our license system. This is how we keep food on our tables.)')
