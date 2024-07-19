from tkinter import *
from tkinter.messagebox import showwarning

#Kelas(obyek) yang memiliki method untuk cek validasi input yang diberikan user
class BarcodeGenerator:
    #Method untuk filtering input pada nama file dan decimal digit
    def validate_input(self, filename, digit_input):
        if not filename.endswith(".eps"):
            showwarning("Wrong input!", "Please enter correct input file format")
            return False

        if len(digit_input) < 12 or len(digit_input) > 13 or not digit_input.isdigit():
            showwarning("Wrong input!", "Please enter correct of digits input")
            return False

        if len(digit_input) == 13 and digit_input[-1] != str(self.last_digit(digit_input)):
            showwarning("Incorrect digit!", f"The last digit must be {self.last_digit(digit_input)}")
            return False
        return True

    #Method untuk menghitung digit terakhir + checksum
    def last_digit(self, digit_input):
        count = 0
        if len(digit_input) == 13:
            digit_input = digit_input[:len(digit_input) - 1]

        for index in range(len(digit_input)):
            if index % 2 != 0:
                count += int(digit_input[index]) * 3
            else:
                count += int(digit_input[index])
        count = 10 - count % 10
        if count == 10:
            count = 0
        return count
    
    #Method yang akan mengembalikan data barcode (jika tidak None)
    def generate_barcode(self, filename, digit_input):
        if not self.validate_input(filename, digit_input):
            return None

        barcode_data = self.EAN13_encode(digit_input)
        if barcode_data is None:
            return None

        return barcode_data
    
    #Method abstrak yang akan di-override pada subclass
    def EAN13_encode(self, digit_input):
        pass #raise NotImplementedError

#Kelas untuk men-encode pada digit valid yang telah diinput
class EAN13BarcodeGenerator(BarcodeGenerator):
    #Method untuk generate binary string yang akan digunakan untuk menampilkan sebuah barcode
    def EAN13_encode(self, digit_input):
        __code_list = ['LLLLLL', 'LLGLGG', 'LLGGLG', 'LLGGGL', 'LGLLGG', 'LGGLLG', 'LGGGLL', 'LGLGLG', 'LGLGGL', 'LGGLGL']
        __L_list = ['0001101', '0011001', '0010011', '0111101', '0100011', '0110001', '0101111', '0111011', '0110111', '0001011']
        __G_list = ['0100111', '0110011', '0011011', '0100001', '0011101', '0111001', '0000101', '0010001', '0001001', '0010111']
        __R_list = ['1110010', '1100110', '1101100', '1000010', '1011100', '1001110', '1010000', '1000100', '1001000', '1110100']

        digit_input = digit_input + str(self.last_digit(digit_input))
        if len(digit_input) == 14:
            digit_input = digit_input[:-1]
        generate_code = __code_list[int(digit_input[0])] + 'RRRRRR'
        digit_input = digit_input[1::]
        binary_list = []

        for index in range(len(digit_input)):
            if generate_code[index] == 'L':
                binary_list.append(__L_list[int(digit_input[index])])
            elif generate_code[index] == 'G':
                binary_list.append(__G_list[int(digit_input[index])])
            elif generate_code[index] == 'R':
                binary_list.append(__R_list[int(digit_input[index])])

        #Menambahkan M(middle) dengan bit pattern 01010
        formatted_list = []
        for i in range(len(binary_list)):
            if i == 6:
                formatted_list.append("M")
            formatted_list.append(binary_list[i])

        return formatted_list

#Main class
class GUI(Tk):
    #Constructor method pada class GUI yang mengambil parameter barcode_generator
    def __init__(self, barcode_generator):
        #Memanggil constructor dari superclass Tk
        super().__init__()
        self.title("EAN-13")
        self.geometry("320x370")
        self.resizable(False, False)
        self.barcode_generator = barcode_generator
        self.file = StringVar()
        self.digit = StringVar()
        self.homepage()

    #Method yang berfungsi menampilkan perintah dan bahan input pada window GUI
    def homepage(self):
        self.file_label = Label(self, text="Save barcode to PS file [eg: EAN13.eps]:", font=("Arial bold", 12))
        self.file_label.pack()
        self.file_input = Entry(self, textvariable=self.file)
        self.file_input.pack()
        self.digit_label = Label(self, text="Enter code (first 12 decimal digits):", font=("Arial bold", 12))
        self.digit_label.pack()
        self.digits_input = Entry(self, textvariable=self.digit)
        self.digits_input.pack()
        self.canvas = Canvas(self, width="300", height="280", bg="white")
        self.canvas.pack()
        self.bind("<Return>", lambda event: self.generate_barcode())
    
    #Mengembalikan value dari method validate_input pada class BarcodeGenerator yang akan digunakan pada class GUI
    def validate_input(self):
        filename = self.file.get()
        digit_input = self.digits_input.get()
        return self.barcode_generator.validate_input(filename, digit_input)

    #Method perintah untuk menampilkan barcode dan saving barcode pada file postscript
    def generate_barcode(self, event=None):
        if not self.validate_input():
            return
        barcode_data = self.barcode_generator.generate_barcode(self.file.get(), self.digit.get())
        if barcode_data is not None:
            self.display_barcode(barcode_data)
            self.save()

    #Method untuk menampilkan barcode pada window GUI
    def display_barcode(self, barcode_data):
        if barcode_data is False:
            return False
        
        self.canvas.delete("all")
        self.canvas.create_text(150, 50, text="EAN-13 Barcode :", font="Times-New-Roman 14 bold")

        #Menampilkan barcode
        x_barcode = 55
        y_barcode = 80
        for i in [1, 0, 1]:
            if i == 1:
                self.canvas.create_line(x_barcode, y_barcode, x_barcode, y_barcode + 130, fill="Blue", width=2)
            x_barcode += 2
        for element in barcode_data:
            for binary in element:
                if binary == 'M':
                    x_barcode += 2
                    self.canvas.create_line(x_barcode, y_barcode, x_barcode, y_barcode + 130, fill="Blue", width=2)
                    x_barcode += 4
                    self.canvas.create_line(x_barcode, y_barcode, x_barcode, y_barcode + 130, fill="Blue", width=2)
                    x_barcode += 2
                elif binary == '1':
                    self.canvas.create_line(x_barcode, y_barcode, x_barcode, y_barcode + 120, fill="Black", width=2)
                x_barcode += 2
        for i in [1, 0, 1]:
            if i == 1:
                self.canvas.create_line(x_barcode, y_barcode, x_barcode, y_barcode + 130, fill="Blue", width=2)
            x_barcode += 2

        #Menampilkan digit yang di bawah barcode
        barcode_number = self.digit.get() + str(self.barcode_generator.last_digit(self.digit.get()))
        if len(barcode_number) == 14:
            barcode_number = barcode_number[:-1]
        self.canvas.create_text(48, 210, text=barcode_number[0], font="Times-New-Roman 12 bold")
        x_digits = 67
        y_digits = 210
        for char in barcode_number[1:7]:
            self.canvas.create_text(x_digits, y_digits, text=char, font="Times-New-Roman 12 bold")
            x_digits += 14
        x_digits += 9
        for char in barcode_number[7:]:
            self.canvas.create_text(x_digits, y_digits, text=char, font="Times-New-Roman 12 bold")
            x_digits += 14

        self.canvas.create_text(142, 235, text=f"Check Digit: {self.barcode_generator.last_digit(self.digit.get())}", font="Times-New-Roman 12 bold", fill="Orange")

    #Method untuk menyimpan barcode pada file postscript
    def save(self):
        if not self.validate_input():
            return
        filename = self.file.get()
        self.canvas.postscript(file=filename)

#Main function
def main():
    gui_barcode = GUI(EAN13BarcodeGenerator())
    gui_barcode.mainloop()

if __name__ == "__main__":
    main()