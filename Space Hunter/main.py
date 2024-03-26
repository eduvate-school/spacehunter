import pygame
import math
import random
import os

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#Loading Images
background = pygame.image.load("assets/background-black.png")
BG = pygame.transform.scale(background,(SCREEN_WIDTH, SCREEN_HEIGHT))

player_img = pygame.image.load('assets/pixel_ship_yellow.png')
player_image = pygame.transform.rotate(player_img, -90)

#Define the path for the subfolders 
assets_enemies = "assets/enemies"
assets_bullets = "assets/bullets"

#Loading Fonts
main_font = pygame.font.SysFont("comic sans", 40)
final_font = pygame.font.SysFont("Lexend", 60)

#Defining Colors
WHITE = (255,255,255)
RED = (255,0,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = player_image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def update(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.rotate()
    
    def rotate(self):
        #retrieves the mouse cursor's position on the screen
        mouse_x, mouse_y = pygame.mouse.get_pos()
        #Calculates the relative distance between the player sprite's center 
        #and the mouse cursor’s position.
        rel_x = mouse_x - self.rect.centerx
        rel_y =  mouse_y - self.rect.centery

        angle = math.degrees(-math.atan2(rel_y, rel_x))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = self.load_images()
        self.image = random.choice(self.images)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        
    def load_images(self):
        images = []
        for filename in os.listdir(assets_enemies):
            if filename.endswith(".png"):  
                image = pygame.image.load(os.path.join(assets_enemies, filename)).convert_alpha()
                images.append(image)
        return images
    
    def update(self, player_rect):
        dx = player_rect.x - self.rect.x
        dy = player_rect.y - self.rect.y                        
        dist = max(abs(dx), abs(dy))
        if dist != 0:
            self.rect.x += dx / dist
            self.rect.y += dy / dist

#Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.bullet_image = self.load_images()
        self.original_image = random.choice(self.bullet_image)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx = dx
        self.dy = dy
        self.speed = 10
        self.rotate()
    
    def load_images(self):
        images = []
        for filename in os.listdir(assets_bullets):
            if filename.endswith(".png"):  
                img = pygame.image.load(os.path.join(assets_bullets, filename)).convert_alpha()
                image = pygame.transform.rotate(img, 90)
                images.append(image)
        return images
    
    def rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x = mouse_x - self.rect.centerx
        rel_y = mouse_y - self.rect.centery
        angle = math.degrees(-math.atan2(rel_y, rel_x))
        self.image = pygame.transform.rotate(self.original_image, angle)               

    def shoot_bullet(self, player_x,player_y):
                # Get mouse x and y
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # get horizontal and vertical distance from player and mouse position
                rel_x = mouse_x - player_x
                rel_y = mouse_y - player_y
                
                # Calculate the length of the vector and then normalize the vector
                distance = math.hypot(rel_x, rel_y)
                dx = rel_x / distance
                dy = rel_y / distance
                return dx,dy
    
    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        if self.rect.bottom < 0:
            self.kill()

#main function
def main():
    pygame.display.set_caption("Space Hunter")

    #game variables
    lives = 10
    score = 0

    player = Player()
    player_group = pygame.sprite.Group()
    player_group.add(player)

    enemy = Enemy()
    enemy_group = pygame.sprite.Group()
    enemy_group.add(enemy)

    bullet = Bullet(player.rect.centerx, player.rect.centery, 0, 0)
    bullet_group = pygame.sprite.Group()

    clock = pygame.time.Clock()

    running = True
    while running:
        
        screen.blit(BG, (0, 0))
        player_group.draw(screen)
        enemy_group.draw(screen)
        bullet_group.draw(screen)

        # Player Movement Event Handling along with detecting boundary collision
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] and player.rect.left > 0:
            dx = -5
        if keys[pygame.K_RIGHT] and player.rect.right < SCREEN_WIDTH:
            dx = 5
        if keys[pygame.K_UP] and player.rect.top > 0:
            dy = -5
        if keys[pygame.K_DOWN] and player.rect.bottom < SCREEN_HEIGHT:
            dy = 5
        player_group.update(dx, dy)
        
        #updating enemy object
        enemy_group.update(player.rect)

        # Handling event for quitting window
        for event in pygame.event.get():
            if event.type == pygame.QUIT or lives <= 0:
                pygame.time.delay(2500)
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button:
                dx, dy = bullet.shoot_bullet(player.rect.centerx,player.rect.centery)
                bullet = Bullet(player.rect.centerx, player.rect.centery, dx, dy)
                bullet_group.add(bullet) 

        bullet_group.update()

         # Check collision between Bullet and Enemy and increase the score by 1
        is_enemykilled = pygame.sprite.groupcollide(bullet_group, enemy_group, True, True)
        if is_enemykilled:
            score += 1

        # Check if all enemies are dead then add more 5 enemies
        if len(enemy_group) == 0:
            for i in range(5):
                enemy = Enemy()
                enemy_group.add(enemy)
        
        #Display Lives
        lives_label = main_font.render("Lives: " + str(lives), 1, RED)
        screen.blit(lives_label, (10, 10))  
        
        # Check collision between Player and Enemy and decrease lives
        if pygame.sprite.spritecollide(player, enemy_group, dokill=True, collided=pygame.sprite.collide_mask):
            lives -= 1

        #Display Score
        score_label = main_font.render("Score: " + str(score), 1, YELLOW)
        screen.blit(score_label, (SCREEN_WIDTH - score_label.get_width() - 10, 10))

        # Show game over and final score if lives == 0 
        game_over_label = final_font.render("Game Over", 1, RED)
        final_score_label = final_font.render("Your Final Score is: " + str(score), 1, WHITE)

        if lives == 0:
            screen.blit(BG, (0, 0))
            screen.blit(game_over_label, (SCREEN_WIDTH/2 - game_over_label.get_width()/2, 150))
            screen.blit(final_score_label, (SCREEN_WIDTH/2 - final_score_label.get_width()/2, 250))

        # Update display
        pygame.display.update()

        clock.tick(60)  

    pygame.quit()

if __name__ == "__main__":
    main()

