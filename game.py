import pygame
import sys
import deck
import db
import locale as lc
from pygame import mixer


pygame.init()
mixer.init()
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
CARD_WIDTH = 100
CARD_HEIGHT = 145
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
FPS = 60

GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GOLD = (255, 215, 0)


screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("SIA'S BLACKJACK TABLE")
clock = pygame.time.Clock()

# fonts
try:
    font = pygame.font.Font('freesansbold.ttf', 32)
    small_font = pygame.font.Font('freesansbold.ttf', 24)
except pygame.error:
    print("Font loading failed. Using system default.")
    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 24)

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color
        self.is_hovered = False

    def draw(self, surface):
        color = (min(self.color[0] + 30, 255), 
                min(self.color[1] + 30, 255), 
                min(self.color[2] + 30, 255)) if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Card:
    def __init__(self, card_data, x, y, face_up=True):
        self.rank = card_data[0]
        self.suit = card_data[1]
        self.value = card_data[2]
        self.x = x
        self.y = y
        self.face_up = face_up
        
    def draw(self, surface):
        #draew card background
        card_rect = pygame.Rect(self.x, self.y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surface, WHITE, card_rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, card_rect, 2, border_radius=5)

        if not self.face_up:
            #draw card back
            pygame.draw.rect(surface, RED, card_rect.inflate(-10, -10), border_radius=3)
            return

        # suit and rank
        suit_symbol = {
            'Hearts': '♥', 'Diamonds': '♦',
            'Clubs': '♣', 'Spades': '♠'
        }[self.suit]
        
        suit_color = RED if self.suit in ['Hearts', 'Diamonds'] else BLACK
        
        # rank
        rank_text = font.render(str(self.rank), True, suit_color)
        surface.blit(rank_text, (self.x + 5, self.y + 5))
        
        # suit
        suit_text = font.render(suit_symbol, True, suit_color)
        surface.blit(suit_text, (self.x + CARD_WIDTH//2 - 15, self.y + CARD_HEIGHT//2 - 15))

class Game:
    def __init__(self):
        self.reset_game()
        self.balance = self.get_starting_balance()
        self.bet = 0
        self.game_phase = "betting"  # betting, playing, dealer_turn, game_over
        
        # create buttons
        button_y = WINDOW_HEIGHT - 100
        self.hit_button = Button(300, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Hit", GREEN)
        self.stand_button = Button(520, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Stand", GREEN)
        self.deal_button = Button(740, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Deal", GREEN)
        
        # bet buttons
        self.bet_buttons = [
            Button(50 + i*120, button_y, 100, BUTTON_HEIGHT, f"${amt}", GOLD)
            for i, amt in enumerate([5, 25, 100, 500])
        ]
        self.bet_amounts = [5, 25, 100, 500]

    def reset_game(self):
        self.deck_of_cards = deck.get_deck()
        deck.shuffle(self.deck_of_cards)
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.player_bust = False
        self.dealer_bust = False
        self.blackjack = False

    def get_starting_balance(self):
        try:
            balance = db.read_money()
        except FileNotFoundError:
            balance = 1000
            db.write_money(balance)
        return balance if balance >= 5 else 1000

    def deal_initial_cards(self):
        self.player_hand = []
        self.dealer_hand = []
        for _ in range(2):
            self.player_hand.append(deck.deal(self.deck_of_cards))
        self.dealer_hand.append(deck.deal(self.deck_of_cards))
        self.game_phase = "playing"

    def hit(self):
        self.player_hand.append(deck.deal(self.deck_of_cards))
        if deck.calculate(self.player_hand) > 21:
            self.player_bust = True
            self.game_phase = "game_over"
            self.balance -= self.bet
            db.write_money(self.balance)

    def dealer_play(self):
        while deck.calculate(self.dealer_hand) < 17:
            self.dealer_hand.append(deck.deal(self.deck_of_cards))
        self.determine_winner()

    def determine_winner(self):
        player_points = deck.calculate(self.player_hand)
        dealer_points = deck.calculate(self.dealer_hand)
        
        if player_points > 21:
            self.balance -= self.bet
        elif dealer_points > 21:
            self.balance += self.bet
        elif player_points > dealer_points:
            self.balance += self.bet
        elif player_points < dealer_points:
            self.balance -= self.bet
            
        db.write_money(self.balance)
        self.game_phase = "game_over"

    def draw(self, surface):
        surface.fill(GREEN)
        balance_text = font.render(f"Balance: ${self.balance}", True, WHITE)
        surface.blit(balance_text, (20, 20))
        if self.bet > 0:
            bet_text = font.render(f"Bet: ${self.bet}", True, WHITE)
            surface.blit(bet_text, (20, 60))
        self.draw_hands(surface)

        if self.game_phase == "betting":
            for button in self.bet_buttons:
                button.draw(surface)
            if self.bet > 0:
                self.deal_button.draw(surface)
        elif self.game_phase == "playing":
            self.hit_button.draw(surface)
            self.stand_button.draw(surface)
        
        if self.game_phase == "game_over":
            self.draw_game_over_message(surface)
            self.deal_button.text = "Play Again"
            self.deal_button.draw(surface)

    def draw_hands(self, surface):

        for i, card_data in enumerate(self.player_hand):
            card = Card(card_data, 300 + i * 60, WINDOW_HEIGHT - 300)
            card.draw(surface)


        for i, card_data in enumerate(self.dealer_hand):
            face_up = self.game_phase == "game_over" or i == 0
            card = Card(card_data, 300 + i * 60, 100, face_up)
            card.draw(surface)

    def draw_game_over_message(self, surface):
        player_points = deck.calculate(self.player_hand)
        dealer_points = deck.calculate(self.dealer_hand)
        
        if self.player_bust:
            message = "Bust! You lose!!"
        elif dealer_points > 21:
            message = "Dealer bust! You win!!!!!!!!"
        elif player_points > dealer_points:
            message = "You win!!!!!!!"
        elif player_points < dealer_points:
            message = "Dealer wins!"
        else:
            message = "Push!"
            
        text = font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        surface.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.game_phase == "betting":
                for i, button in enumerate(self.bet_buttons):
                    if button.handle_event(event):
                        bet_amount = self.bet_amounts[i]
                        if bet_amount <= self.balance:
                            self.bet += bet_amount
                
                if self.deal_button.handle_event(event) and self.bet > 0:
                    self.deal_initial_cards()
                    
            elif self.game_phase == "playing":
                if self.hit_button.handle_event(event):
                    self.hit()
                elif self.stand_button.handle_event(event):
                    self.dealer_play()
                    
            elif self.game_phase == "game_over":
                if self.deal_button.handle_event(event):
                    self.reset_game()
                    self.bet = 0
                    self.game_phase = "betting"

        elif event.type == pygame.MOUSEMOTION:
            # Update button hover states
            for button in self.bet_buttons + [self.hit_button, self.stand_button, self.deal_button]:
                button.handle_event(event)

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
                
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()