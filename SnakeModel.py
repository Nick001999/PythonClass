
import random


class SnakeModel:
    def __init__(self):
        self.lives = 5
        self.body = [
            [200, 200],
            [200, 210],
            [200, 220],
            [200, 230]
        ]
        self.direction = "Up"
        self.fruit = [0, 0]
        self.set_fruit_position()

    def set_fruit_position(self):
        x = random.randint(10, 390)         #Ex 1, changed from 1,400 to 10,390
        y = random.randint(10, 390)         #Ex 1, changed from 1,400 to 10,390
        xd = x % 10
        yd = y % 10
        x = x - xd
        y = y - yd
        self.fruit = [x, y]

    def move_body_parts(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i][0] = self.body[i - 1][0]
            self.body[i][1] = self.body[i - 1][1]

    def eat_fruit(self):
        if self.fruit[0] == self.body[0][0] and self.fruit[1] == self.body[0][1]:
            self.body.append([self.body[-1][0], self.body[-1][1]])
            self.set_fruit_position()

    def move_up(self):
        if self.direction != "Down":
            if self.body[0][0] != 0 and self.body[0][1] != 0:
                self.move_body_parts()
                self.body[0][1] -= 10
                self.direction = "Up"
                self.eat_fruit()
            else:
                self.lives -= 1

    def move_down(self):
        if self.direction != "Up":
            if self.body[0][0] != 390 and self.body[0][1] != 390:
                self.move_body_parts()
                self.body[0][1] += 10
                self.direction = "Down"
                self.eat_fruit()
            else:
                self.lives -= 1

    def move_left(self):
        if self.direction != "Right":
            if self.body[0][0] != 0 and self.body[0][1] != 0:
                self.move_body_parts()
                self.body[0][0] -= 10
                self.direction = "Left"
                self.eat_fruit()
            else:
                self.lives -= 1

    def move_right(self):
        if self.direction != "Left":
            if self.body[0][0] != 390 and self.body[0][1] != 390:
                self.move_body_parts()
                self.body[0][0] += 10
                self.direction = "Right"
                self.eat_fruit()
            else:
                self.lives -= 1


if __name__ == '__main__':
    model = SnakeModel()
    print(model.body)
    model.move_up()
    print(model.body)
