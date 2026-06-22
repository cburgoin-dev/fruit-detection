import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

import cv2
import threading
import time

from config.prices import FRUIT_PRICES
from config.translations import FRUIT_TRANSLATIONS
from config.settings import CAMERA_INDEX
from services.tensorflow_service import TensorflowService
from services.serial_service import SerialService


class FruitWindow:

    def __init__(self, root):

        self.root = root
        self.root.title("Sistema de Detección de Frutas")
        self.root.geometry("920x680")
        self.root.resizable(False, False)

        self.detector = TensorflowService()

        self.serial_service = SerialService()
        self.serial_service.connect()

        self.cap = None

        self.video_thread = None

        self.is_running = False

        self.last_detected_fruit = None
        self.last_detected_weight = 0.0
        self.last_detected_price = 0.0

        self.total_var = tk.StringVar(value="TOTAL: $0.00")

        if self.serial_service.connection:
            status = "Balanza: Conectada"

        else:
            status = (
                "Balanza: No detectada "
                "| Demo Mode"
            )

        self.balanza_status = tk.StringVar(value=status)

        self.demo_mode = not bool(
            self.serial_service.connection
        )

        self.input_mode = "camera"

        self.current_image = None

        self.mode_var = tk.StringVar(
            value="Modo: Cámara"
        )

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)

        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side="left")

        self.sidebar_frame = ttk.Frame(self.main_frame)
        self.sidebar_frame.pack(
            side="left",
            fill="y",
            padx=(10, 0)
        )

        self.create_video_panel()

        placeholder = Image.new(
            "RGB",
            (600, 400),
            color=(40, 40, 40)
        )

        self.show_image(placeholder)

        self.create_sidebar()
        self.create_cart_panel()

        if self.serial_service.connection:

            self.serial_thread = threading.Thread(
                target=self.serial_service.loop,
                daemon=True
            )

            self.serial_thread.start()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_closing
        )

    def create_video_panel(self):

        video_container = ttk.LabelFrame(
            self.left_frame,
            text="Cámara y Detección en Tiempo Real"
        )

        video_container.pack(fill="x")

        self.video_frame = tk.Frame(
            video_container,
            bg="black",
            width=600,
            height=400
        )

        self.video_frame.pack(
            padx=5,
            pady=5
        )

        self.video_frame.pack_propagate(False)

        self.video_label = tk.Label(
            self.video_frame,
            bg="black"
        )

        self.video_label.pack(
            fill="both",
            expand=True
        )

    def create_action_button(
        self,
        parent,
        text,
        command,
        color="#2d2d2d",
        active="#404040"
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 10, "bold"),
            bg=color,
            fg="white",
            activebackground=active,
            activeforeground="white",
            width=16,
            height=1,
            relief="raised",
            bd=1,
            cursor="hand2"
        )

    def create_sidebar(self):

        sidebar = ttk.LabelFrame(
            self.sidebar_frame,
            text="Detalles y Acciones"
        )

        sidebar.pack(
            fill="both",
            expand=True
        )

        sidebar.configure(width=250)

        info = tk.Frame(
            sidebar,
        )

        info.pack(
            fill="x",
            padx=20
        )

        self.lbl_mode_header = tk.Label(
            info,
            textvariable=self.mode_var,
            font=("Arial", 13, "bold"),
        )

        self.lbl_mode_header.pack(
            anchor="w",
            pady=(0, 8)
        )

        self.lbl_fruit = tk.Label(
            info,
            text="Fruta: N/A",
        )

        self.lbl_weight = tk.Label(
            info,
            text="Peso: N/A",
        )

        self.lbl_price = tk.Label(
            info,
            text="Precio/kg: N/A",
        )

        self.lbl_subtotal = tk.Label(
            info,
            text="Subtotal: N/A",
        )

        self.lbl_scale = tk.Label(
            info,
            textvariable=self.balanza_status,
        )

        for label in [

            self.lbl_fruit,
            self.lbl_weight,
            self.lbl_price,
            self.lbl_subtotal,
            self.lbl_scale

        ]:

            label.pack(
                anchor="w",
                pady=(0, 1)
            )

        if self.demo_mode:

            self.demo_weight_label = tk.Label(
                info,
                text="Peso simulado: 500 g",
                font=("Arial", 11, "bold")
            )

            self.demo_weight_label.pack(
                anchor="w",
                pady=(6, 2)
            )

            self.demo_weight = tk.DoubleVar(value=500)

            self.demo_weight.trace_add(
                "write",
                self.update_demo_weight
            )

            ttk.Scale(
                info,
                from_=0,
                to=2000,
                variable=self.demo_weight,
                orient="horizontal"
            ).pack(
                fill="x",
                pady=2
            )

            ticks = tk.Frame(
                info,
            )

            ticks.pack(fill="x")

            tk.Label(
                ticks,
                text="0 g",
            ).pack(side="left")

            tk.Label(
                ticks,
                text="2 kg",
            ).pack(side="right")

        ttk.Separator(sidebar).pack(
            fill="x",
            padx=20,
            pady=20
        )

        controls = tk.Frame(
            sidebar,
        )

        controls.pack(
            fill="x",
            padx=20
        )

        tk.Label(
            controls,
            text="ENTRADA",
            font=("Arial", 9, "bold")
        ).pack(pady=(0, 6))

        entrada = [

            ("Abrir Imagen",
            self.load_image,
            "#404040",
            "#555555"),

            ("Iniciar Cámara",
            self.activate_camera,
            "#404040",
            "#555555"),

            ("Detener Cámara",
            self.stop_camera,
            "#404040",
            "#555555")
        ]

        for text, command, color, active in entrada:

            self.create_action_button(
                controls,
                text,
                command,
                color,
                active
            ).pack(pady=3)

        ttk.Separator(controls).pack(
            fill="x",
            padx=10,
            pady=10
        )

        tk.Label(
            controls,
            text="CARRITO",
            font=("Arial", 9, "bold")
        ).pack(pady=(0, 6))

        carrito = [

            ("Agregar Producto",
            self.add_fruit,
            "#404040",
            "#555555"),

            ("Eliminar Producto",
            self.remove_fruit,
            "#404040",
            "#555555")
        ]

        for text, command, color, active in carrito:

            self.create_action_button(
                controls,
                text,
                command,
                color,
                active
            ).pack(pady=3)

        ttk.Separator(controls).pack(
            fill="x",
            padx=10,
            pady=10
        )

        tk.Label(
            controls,
            text="COMPRA",
            font=("Arial", 9, "bold")
        ).pack(pady=(0, 6))

        self.create_action_button(
            controls,
            "Finalizar Compra",
            self.finalize_order,
            "#404040",
            "#555555"
        ).pack(pady=3)

        self.create_action_button(
            controls,
            "Cancelar Compra",
            self.cancel_order,
            "#DC2626",
            "#991B1B"
        ).pack(pady=3)

    def create_cart_panel(self):

        cart = ttk.LabelFrame(
            self.left_frame,
            text="Carrito de Compras"
        )

        cart.pack(
            fill="x",
            pady=(10, 0)
        )

        self.receipt_tree = ttk.Treeview(
            cart,
            columns=(
                "fruit",
                "weight",
                "price"
            ),
            show="headings",
            height=6
        )

        self.receipt_tree.heading(
            "fruit",
            text="Fruta"
        )

        self.receipt_tree.heading(
            "weight",
            text="Peso (kg)"
        )

        self.receipt_tree.heading(
            "price",
            text="Total ($)"
        )

        self.receipt_tree.column(
            "fruit",
            width=300,
            anchor="center"
        )

        self.receipt_tree.column(
            "weight",
            width=150,
            anchor="center"
        )

        self.receipt_tree.column(
            "price",
            width=150,
            anchor="center"
        )

        self.receipt_tree.pack(
            fill="x",
            padx=5,
            pady=5
        )

        ttk.Label(
            cart,
            textvariable=self.total_var,
            font=("Arial", 16, "bold")
        ).pack(
            anchor="e",
            padx=10,
            pady=5
        )

    def video_loop(self):

        while self.is_running and self.cap:

            if self.input_mode != "camera":
                time.sleep(0.1)
                continue

            if not self.cap:
                break

            ret, frame = self.cap.read()

            if not ret:

                time.sleep(0.1)

                continue

            fruit = self.detector.predict(frame)

            if self.demo_mode:

                weight_kg = (
                    self.demo_weight.get() / 1000
                )

            else:

                weight_kg = (
                    self.serial_service.weight_g / 1000
                )

            price_kg = FRUIT_PRICES.get(
                fruit,
                20.0
            )

            subtotal = weight_kg * price_kg

            self.last_detected_fruit = fruit
            self.last_detected_weight = weight_kg
            self.last_detected_price = subtotal

            self.root.after(
                0,
                lambda:
                self.update_details(
                    fruit,
                    weight_kg,
                    price_kg,
                    subtotal
                )
            )

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            image = Image.fromarray(frame_rgb)

            image = image.resize(
                (600, 400)
            )

            self.root.after(
                0,
                lambda img=image:
                self.show_image(img)
            )

            time.sleep(0.05)

    def update_details(
        self,
        fruit,
        weight,
        price,
        subtotal
    ):

        fruit_name = FRUIT_TRANSLATIONS.get(
            fruit,
            fruit
        )

        self.lbl_fruit.config(
            text=f"Fruta: {fruit_name}"
        )

        self.lbl_weight.config(
            text=f"Peso: {weight:.3f} kg"
        )

        self.lbl_price.config(
            text=f"Precio/kg: ${price:.2f}"
        )

        self.lbl_subtotal.config(
            text=f"Subtotal: ${subtotal:.2f}"
        )

    def update_demo_weight(self, *args):

        gramos = int(
            self.demo_weight.get()
        )

        self.demo_weight_label.config(
            text=f"Peso simulado: {gramos} g"
        )

    def load_image(self):

        self.stop_camera()

        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                (
                    "Imágenes",
                    "*.jpg *.jpeg *.png"
                )
            ]
        )

        if not path:
            return

        frame = cv2.imread(path)

        self.current_image = frame.copy()

        if frame is None:

            messagebox.showerror(
                "Error",
                "No se pudo abrir la imagen."
            )

            return

        self.input_mode = "image"

        self.mode_var.set(
            "Modo: Imagen cargada"
        )

        fruit = self.detector.predict(frame)

        if self.demo_mode:

            weight_kg = (
                self.demo_weight.get() / 1000
            )

        else:

            weight_kg = (
                self.serial_service.weight_g / 1000
            )

        price_kg = FRUIT_PRICES.get(
            fruit,
            20.0
        )

        subtotal = weight_kg * price_kg

        self.last_detected_fruit = fruit
        self.last_detected_weight = weight_kg
        self.last_detected_price = subtotal

        self.update_details(
            fruit,
            weight_kg,
            price_kg,
            subtotal
        )

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(frame_rgb)

        image = image.resize(
            (600, 400)
        )

        self.show_image(image)

    def show_image(self, pil_image):

        image_tk = ImageTk.PhotoImage(pil_image)

        self.video_label.imgtk = image_tk

        self.video_label.configure(
            image=image_tk
        )

    def activate_camera(self):

        if self.is_running:
            return

        self.cap = cv2.VideoCapture(CAMERA_INDEX)

        if not self.cap.isOpened():

            messagebox.showerror(
                "Error",
                "No se pudo abrir la cámara."
            )

            return

        self.input_mode = "camera"

        self.is_running = True

        self.mode_var.set(
            "Modo: Cámara"
        )

        self.video_thread = threading.Thread(
            target=self.video_loop,
            daemon=True
        )

        self.video_thread.start()

    def stop_camera(self):

        self.is_running = False

        if self.cap:

            self.cap.release()

            self.cap = None

        self.mode_var.set(
            "Modo: Cámara detenida"
        )

    def add_fruit(self):

        if not self.last_detected_fruit:

            messagebox.showwarning(
                "Advertencia",
                "No se ha detectado ninguna fruta."
            )

            return

        if self.last_detected_weight <= 0:

            messagebox.showwarning(
                "Advertencia",
                "Peso en balanza es 0. Coloque el producto."
            )

            return

        self.receipt_tree.insert(
            "",
            "end",
            values=(
                FRUIT_TRANSLATIONS.get(
                    self.last_detected_fruit,
                    self.last_detected_fruit
                ),
                f"{self.last_detected_weight:.3f}",
                f"{self.last_detected_price:.2f}"
            )
        )

        self.update_total()

    def remove_fruit(self):

        selected = self.receipt_tree.focus()

        if selected:

            self.receipt_tree.delete(selected)

            self.update_total()

        else:

            messagebox.showwarning(
                "Advertencia",
                "Selecciona una fruta para eliminar."
            )

    def finalize_order(self):

        total = self.calculate_total()

        if total <= 0:

            messagebox.showwarning(
                "Advertencia",
                "El carrito está vacío."
            )

            return

        messagebox.showinfo(
            "Recibo",
            f"Total a pagar: ${total:.2f}"
        )

        self.cancel_order()

    def cancel_order(self):

        for item in self.receipt_tree.get_children():

            self.receipt_tree.delete(item)

        self.update_total()

    def calculate_total(self):

        total = 0

        for item in self.receipt_tree.get_children():

            total += float(
                self.receipt_tree.item(
                    item,
                    "values"
                )[2]
            )

        return total

    def update_total(self):

        total = self.calculate_total()

        self.total_var.set(
            f"TOTAL: ${total:.2f}"
        )

    def on_closing(self):

        self.is_running = False

        if self.cap and self.cap.isOpened():

            self.cap.release()

        if self.serial_service.connection:

            self.serial_service.connection.close()

        self.root.destroy()