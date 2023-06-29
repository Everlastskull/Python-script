import random

def discover_secret_number():
    secret_number = random.randint(1, 100)
    attempts = 0
    
    while True:
        guess = int(input("Entrez votre proposition : "))
        attempts += 1
        
        if guess < secret_number:
            print("Trop bas ! Réessayez.")
        elif guess > secret_number:
            print("Trop haut ! Réessayez.")
        else:
            print(f"Félicitations ! Vous avez trouvé le nombre secret en {attempts} tentative(s) !")
            break

discover_secret_number()