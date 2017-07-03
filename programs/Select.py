import random

fact_list = ["Did you know that Sonic 3 isn't the 3rd game in the series? Sonic CD was released between Sonic 2 and 3, which is why all levels have the roman numeral 'III' at the start.",
            "Two bosses in *Shadow the Hedgehog*, Blue Falcon and Black Bull, are references to Nintendo's F-Zero series. SEGA developed the GameCube title *F-Zero GX* shortly before the release of Shadow.",
            "In the Dreamcast version of *Sonic Adventure 2*, Big the Cat can be seen hidden throughout the levels and in cutscenes. However, almost all of his appearances were removed for the GameCube version.",
            "The theme of Ice Cap Zone in *Sonic 3* is actually an instrumental version of the unreleased song *Hard Time* by the Jetzons. The keyboardist of the band, Bruce Buxor, later worked on Sonic 3 and added the song to the game.",
            "Michael Jackson briefly worked on the soundtrack of *Sonic 3*, but left the project after a short while, and doesn't appear in the credits of the game. SEGA has never confirmed this, but it's believed Jackson left after being disappointed with the Genesis sound chip.",
            "Several chaos in *Sonic Adventure 2* can be made to look like SEGA characters. Chaos looking like Sonic, Shadow, and NiGHTS can be raised in-game, and a Tails chao can be found and transferred over from a copy of *Phantasy Star Online*. Data for Knuckles and Amy chaos are also in the game, but cannot be accessed without hacking.",
            "Many tracks from *Sonic 3D Blast* were reused in later games. The theme of Green Grove Zone was resued as Windy Hill in *Sonic Adventure*, the prologue theme became Twinkle Park, and Panic Puppet Zone was remixed into Lost Impact in *Shadow the Hedgehog.",
            "Every zone in Sonic 1 has three acts, with the exception of Scrap Brain Zone, the industrial level. It's third act is essentially Labyrinth Zone Act 4. Because of this, the industrial level in Sonic 2, Metropolis Zone, has an additional act than the other levels.",
            "References to SEGA's other series *NiGHTS* can be seen in the Adventure games. There is a NiGHTS pinball section of Casinopolis in *Sonic Adventure*, there is a NiGHTS tower in Radical Highway in *Sonic Adventure 2*, and a chao resembling NiGHTS can be raised in the games.",
            "Murals have been commonly used in the Sonic games for foreshadowing. In *Sonic & Knuckles* a mural depicting Doomsday Zone can be seen during in Hidden Palace Zone. In *Sonic Adventure* a cutscene at the end of Lost World shows an image of Perfect Chaos, and in *Sonic Adventure 2* a mural in the central room of Death Chamber shows the boss King Boom Boo.",
            "Did you know that Sonic 4 is really terrible?",
            "As an easter egg, both Metal Sonic (the boss from Sonic CD) and Mecha Sonic (Knuckles' final boss in Sonic & Knuckles) can be seen under repair in Eggman's base in Sonic Adventure.",
            "GUN soldiers in *Shadow the Hedgehog* can occasionally be heard yelling 'Mr. Yuji Naka is alright!', a reference to Sonic series creator, Yuji Naka.",
            "During development of *Sonic 3*, game designers quickly realized that the game was becoming too large to fit onto a standard cartridge. To fix the problem, the game was split into two games, Sonic 3 and Sonic & Knuckles. S&K featured a special 'lock-on cart' which had a slot on top to allow players to plug other Genesis games into it, unlocking additonal content.",
            "The original Sonic game only had 6 Chaos Emeralds. Earning all 6 would simply earn you a different ending. In Sonic 2, a 7th emerald was added as was the transformation to Super Sonic.",
            "During *Sonic Heroes* and *Shadow the Hedgehog*, a number of Shadow Androids are shown, casting doubt onto whether the playable character is the Shadow from *Sonic Adventure 2*. However, during the Devil Doom fight, a rare piece of dialogue from Dr. Eggman can play, confirming Shadow's identity. The Shadow Android subplot would never be mentioned again.",
            "In *Twilight Princess*, the name of the species Ooccoo is a reference to Link's green color in the original *Legend of Zelda*, which has a hex code of #00CC00... wait, this isn't a Sonic fact!",
            "It is believed that Big's fishing sections were added to *Sonic Adventure* due to the popularity of *SEGA's Bass Fishing* at the time."]

def ban(user_list, author):
    rand_user = random.choice(list(user_list)).name
    ban_list = ["You got it, banning {}".format(rand_user), 
                "Not a problem, banning {}".format(rand_user), 
                "You're the boss, banning {}".format(rand_user), 
                "Ugh *fine*, banning {}".format(rand_user),
                "*YOU'RE NOT MY MOM*",
                "No. I'm gonna ban *you* {}".format(author),
                "Now banning {} :smiling_imp:".format(author)]
    return random.choice(ban_list)

def fact():
    return random.choice(fact_list)