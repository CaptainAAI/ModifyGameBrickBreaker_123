import tkinter as tk  # Mengimpor modul tkinter untuk membuat antarmuka grafis
import random  # Mengimpor modul random untuk menghasilkan nilai acak
import pygame  # Mengimpor modul pygame untuk memainkan efek suara

# Inisialisasi mixer pygame untuk efek suara
pygame.mixer.init()

# Memuat file suara untuk efek tertentu
brick_hit_sound = pygame.mixer.Sound("brick_hit.wav")  # Suara saat brick terkena
paddle_hit_sound = pygame.mixer.Sound("paddle_hit.wav")  # Suara saat paddle terkena
powerup_sound = pygame.mixer.Sound("powerup.wav")  # Suara saat power-up diaktifkan


# Kelas dasar untuk semua objek dalam permainan
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas  # Canvas tempat objek akan digambar
        self.item = item  # Referensi ke objek yang digambar di canvas

    def get_position(self):
        return self.canvas.coords(self.item)  # Mengambil koordinat posisi objek

    def move(self, x, y):
        self.canvas.move(self.item, x, y)  # Memindahkan objek ke arah x, y tertentu

    def delete(self):
        self.canvas.delete(self.item)  # Menghapus objek dari canvas


# Kelas untuk bola dalam permainan
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10  # Radius bola
        self.direction = [1, -1]  # Arah gerakan bola
        self.speed = 5  # Kecepatan bola
        # Membuat lingkaran untuk bola
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')  # Bola berwarna putih
        super(Ball, self).__init__(canvas, item)  # Memanggil constructor kelas induk

    def update(self):
        coords = self.get_position()  # Mendapatkan posisi bola
        width = self.canvas.winfo_width()  # Mendapatkan lebar canvas
        # Membalik arah horizontal jika bola mengenai sisi kiri/kanan
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        # Membalik arah vertikal jika bola mengenai sisi atas
        if coords[1] <= 0:
            self.direction[1] *= -1
        # Menghitung perpindahan bola berdasarkan arah dan kecepatan
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)  # Memindahkan bola

    def collide(self, game_objects):
        coords = self.get_position()  # Mendapatkan posisi bola
        x = (coords[0] + coords[2]) * 0.5  # Mendapatkan posisi horizontal tengah bola
        if len(game_objects) > 1:  # Jika bertabrakan dengan lebih dari satu objek
            self.direction[1] *= -1  # Membalik arah vertikal
        elif len(game_objects) == 1:  # Jika hanya satu objek
            game_object = game_objects[0]  # Objek yang bertabrakan
            coords = game_object.get_position()  # Mendapatkan posisi objek
            if x > coords[2]:  # Jika bola di sisi kanan objek
                self.direction[0] = 1
            elif x < coords[0]:  # Jika bola di sisi kiri objek
                self.direction[0] = -1
            else:  # Jika bola di tengah objek
                self.direction[1] *= -1  # Membalik arah vertikal

        for game_object in game_objects:  # Mengecek semua objek yang bertabrakan
            if isinstance(game_object, Brick):  # Jika objek adalah Brick
                game_object.hit()  # Mengurangi hit point Brick
                pygame.mixer.Sound.play(brick_hit_sound)  # Memainkan suara brick


# Kelas untuk paddle dalam permainan
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80  # Lebar paddle
        self.height = 10  # Tinggi paddle
        self.ball = None  # Bola yang terhubung dengan paddle
        # Membuat persegi panjang untuk paddle
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')  # Paddle berwarna oranye
        super(Paddle, self).__init__(canvas, item)  # Memanggil constructor kelas induk

    def set_ball(self, ball):
        self.ball = ball  # Mengatur bola yang terhubung dengan paddle

    def move(self, offset):
        coords = self.get_position()  # Mendapatkan posisi paddle
        width = self.canvas.winfo_width()  # Mendapatkan lebar canvas
        # Memastikan paddle tidak keluar dari batas canvas
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)  # Memindahkan paddle
            if self.ball is not None:  # Jika ada bola terhubung
                self.ball.move(offset, 0)  # Memindahkan bola


# Kelas untuk brick dalam permainan
class Brick(GameObject):
    COLORS = {1: '#4535AA', 2: '#ED639E', 3: '#8FE1A2'}  # Warna berdasarkan hit point

    def __init__(self, canvas, x, y, hits):
        self.width = 75  # Lebar brick
        self.height = 20  # Tinggi brick
        self.hits = hits  # Jumlah hit point brick
        color = Brick.COLORS[hits]  # Warna sesuai hit point
        # Membuat persegi panjang untuk brick
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')  # Brick diberi tag 'brick'
        super(Brick, self).__init__(canvas, item)  # Memanggil constructor kelas induk

    def hit(self):
        self.hits -= 1  # Mengurangi hit point brick
        if self.hits == 0:  # Jika hit point habis
            self.delete()  # Menghapus brick
            self.canvas.master.score += 10  # Menambah skor pemain
        else:  # Jika masih ada hit point
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])  # Mengubah warna brick


# Kelas untuk power-up dalam permainan
class PowerUp(GameObject):
    def __init__(self, canvas, x, y, effect):
        self.effect = effect  # Efek power-up
        # Membuat lingkaran untuk power-up
        item = canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill='yellow', tags='powerup')
        super().__init__(canvas, item)  # Memanggil constructor kelas induk

    def activate(self, game):
        pygame.mixer.Sound.play(powerup_sound)  # Memainkan suara power-up
        if self.effect == "paddle_size":  # Efek memperbesar paddle
            game.paddle.width *= 1.5  # Memperbesar lebar paddle
            coords = game.paddle.get_position()  # Mendapatkan posisi paddle
            # Memperbarui koordinat paddle
            game.canvas.coords(game.paddle.item, coords[0], coords[1],
                               coords[0] + game.paddle.width, coords[3])
        elif self.effect == "extra_life":  # Efek menambah nyawa
            game.lives += 1  # Menambah jumlah nyawa pemain
            game.update_hud()  # Memperbarui tampilan HUD
        elif self.effect == "extra_ball":  # Efek menambah bola
            game.add_extra_ball()  # Menambah bola
        self.delete()  # Menghapus power-up dari canvas

# Kelas utama untuk permainan
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)  # Memanggil constructor Frame tkinter
        self.lives = 3  # Jumlah nyawa pemain
        self.level = 1  # Level awal permainan
        self.score = 0  # Skor awal pemain
        self.width = 610  # Lebar canvas permainan
        self.height = 400  # Tinggi canvas permainan
        # Membuat canvas sebagai area permainan
        self.canvas = tk.Canvas(self, bg='#D6D1F5',
                                width=self.width,
                                height=self.height)
        self.canvas.pack()  # Menempatkan canvas pada frame
        self.pack()  # Menempatkan frame ke window utama

        self.items = {}  # Dictionary untuk menyimpan semua objek permainan
        self.ball = None  # Referensi awal untuk bola
        self.paddle = Paddle(self.canvas, self.width / 2, 326)  # Membuat paddle di posisi awal
        self.items[self.paddle.item] = self.paddle  # Menambahkan paddle ke dictionary objek
        self.setup_bricks()  # Mengatur brick pada level awal

        self.hud = None  # Elemen untuk tampilan informasi HUD
        self.setup_game()  # Mengatur elemen permainan awal
        self.canvas.focus_set()  # Mengatur fokus pada canvas untuk menerima input
        # Mengikat tombol panah kiri dan kanan untuk menggerakkan paddle
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        self.add_ball()  # Menambahkan bola awal
        self.update_hud()  # Memperbarui informasi HUD
        # Menampilkan teks instruksi awal
        self.text = self.draw_text(300, 200, 'Press Space to start')
        # Mengatur tombol spasi untuk memulai permainan
        self.canvas.bind('<space>', lambda _: self.start_game())

    def setup_bricks(self):
        # Mengatur brick di canvas sesuai level awal
        for x in range(5, self.width - 5, 75):  # Menentukan posisi horizontal
            self.add_brick(x + 37.5, 50, 3)  # Baris pertama dengan 3 hit
            self.add_brick(x + 37.5, 70, 2)  # Baris kedua dengan 2 hit
            self.add_brick(x + 37.5, 90, 1)  # Baris ketiga dengan 1 hit

    def add_ball(self):
        if self.ball is not None:  # Jika bola sudah ada, hapus bola sebelumnya
            self.ball.delete()
        paddle_coords = self.paddle.get_position()  # Mendapatkan posisi paddle
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5  # Menghitung posisi tengah paddle
        self.ball = Ball(self.canvas, x, 310)  # Membuat bola baru
        self.paddle.set_ball(self.ball)  # Menghubungkan bola dengan paddle

    def add_extra_ball(self):
        # Menambahkan bola tambahan di atas paddle
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        new_ball = Ball(self.canvas, x, 310)
        self.items[new_ball.item] = new_ball  # Menyimpan bola baru ke dictionary objek

    def add_brick(self, x, y, hits):
        # Menambahkan brick ke canvas pada posisi tertentu
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick  # Menyimpan brick ke dictionary objek

    def update_hud(self):
        # Memperbarui teks HUD dengan informasi permainan
        text = f'Lives: {self.lives} | Level: {self.level} | Score: {self.score}'
        if self.hud is None:  # Jika HUD belum ada, buat teks baru
            self.hud = self.draw_text(50, 20, text, 15)
        else:  # Jika sudah ada, perbarui teks
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')  # Menghapus pengikatan tombol spasi
        self.canvas.delete(self.text)  # Menghapus teks instruksi awal
        self.paddle.ball = None  # Memutuskan hubungan bola dari paddle
        self.game_loop()  # Memulai loop permainan

    def game_loop(self):
        self.check_collisions()  # Mengecek tabrakan antara bola dan objek
        num_bricks = len(self.canvas.find_withtag('brick'))  # Menghitung jumlah brick yang tersisa
        if num_bricks == 0:  # Jika semua brick habis
            self.level_up()  # Pindah ke level berikutnya
        elif self.ball.get_position()[3] >= self.height:  # Jika bola keluar dari bawah
            self.ball.speed = None  # Menghentikan bola
            self.lives -= 1  # Mengurangi nyawa pemain
            if self.lives < 0:  # Jika nyawa habis
                self.save_high_score()  # Menyimpan skor tertinggi
                self.draw_text(300, 200, 'Game Over!')  # Menampilkan teks Game Over
            else:  # Jika masih ada nyawa
                self.after(1000, self.setup_game)  # Menunggu 1 detik sebelum mengatur ulang permainan
        else:
            self.ball.update()  # Memperbarui posisi bola
            self.after(50, self.game_loop)  # Memanggil game loop setiap 50 ms

    def level_up(self):
        self.canvas.delete('brick')  # Menghapus semua brick dari canvas
        self.level += 1  # Meningkatkan level
        # Menampilkan teks level
        self.text = self.draw_text(300, 200, f'Level {self.level}')
        self.ball.speed += 2  # Meningkatkan kecepatan bola
        # Mengubah warna latar belakang secara acak
        self.canvas.config(bg=random.choice(['#F5D6D1', '#D6F5D1', '#D1D6F5']))
        # Menunggu 1 detik sebelum menambahkan brick baru dan memulai ulang permainan
        self.after(1000, lambda: [self.setup_bricks(), self.setup_game()])

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)  # Mengatur font teks
        return self.canvas.create_text(x, y, text=text, font=font)  # Menampilkan teks di canvas

    def check_collisions(self):
        ball_coords = self.ball.get_position()  # Mendapatkan posisi bola
        items = self.canvas.find_overlapping(*ball_coords)  # Mencari objek yang bertabrakan dengan bola
        objects = [self.items[x] for x in items if x in self.items]  # Memfilter objek yang valid
        self.ball.collide(objects)  # Memproses tabrakan bola dengan objek
        for item in items:  # Mengecek semua objek yang bertabrakan
            if "brick" in self.canvas.gettags(item) and random.random() < 0.2:
                # Menambahkan power-up secara acak
                powerup = PowerUp(self.canvas, ball_coords[0], ball_coords[1], "extra_life")
                self.items[powerup.item] = powerup  # Menyimpan power-up ke dictionary objek

    def save_high_score(self):
        try:
            with open("highscore.txt", "r") as file:  # Membaca skor tertinggi dari file
                high_score = int(file.read())
        except FileNotFoundError:  # Jika file tidak ditemukan
            high_score = 0

        if self.score > high_score:  # Jika skor pemain lebih tinggi
            with open("highscore.txt", "w") as file:  # Menyimpan skor baru
                file.write(str(self.score))


# Bagian utama program
if __name__ == '__main__':
    root = tk.Tk()  # Membuat jendela utama tkinter
    root.title('Break Those Bricks!, Halo Lord AAI')  # Memberi judul jendela
    game = Game(root)  # Membuat instance permainan
    game.mainloop()  # Menjalankan loop utama tkinter
