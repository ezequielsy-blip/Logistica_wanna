import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import QLabel
from kivy.uix.textinput import TextInput
from kivy.uix.button import QPushButton
from kivy.uix.recycleview import RecycleView
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from supabase import create_client

# --- CONFIGURACIÓN ---
URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

class MobileMegazord(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.supabase = create_client(URL, KEY)
        self.padding = 10
        self.spacing = 10
        
        # Fondo Gris Claro
        from kivy.core.window import Window
        Window.clearcolor = get_color_from_hex('#f2f2f2')

        # 1. ENCABEZADO: TOTAL (Tu pedido especial)
        self.lbl_total = QLabel(
            text="STOCK TOTAL: 0",
            size_hint_y=None, height=120,
            font_size='30sp', bold=True,
            color=(1, 1, 1, 1)
        )
        # Fondo azul para el total
        with self.lbl_total.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(rgba=get_color_from_hex('#1e40af'))
            self.rect = RoundedRectangle(pos=self.lbl_total.pos, size=self.lbl_total.size, radius=[10])
        self.lbl_total.bind(pos=self._update_rect, size=self._update_rect)
        self.add_widget(self.lbl_total)

        # 2. BUSCADOR
        self.txt_busqueda = TextInput(
            hint_text="🔍 BUSCAR CÓDIGO O NOMBRE...",
            size_hint_y=None, height=100,
            multiline=False, font_size='20sp'
        )
        self.txt_busqueda.bind(text=self.on_search_change)
        self.add_widget(self.txt_busqueda)

        # 3. LISTA DE RESULTADOS (Simplificada para cel)
        self.add_widget(QLabel(text="RESULTADOS:", size_hint_y=None, height=40, color=(0,0,0,1)))
        self.rv = RecycleView()
        # Aquí iría la lógica de la lista...
        self.add_widget(self.rv)

        # 4. BOTÓN REGISTRAR
        self.btn_registrar = QPushButton(
            text="REGISTRAR MOVIMIENTO",
            size_hint_y=None, height=120,
            background_color=get_color_from_hex('#1e40af'),
            background_normal='',
            font_size='22sp', bold=True
        )
        self.add_widget(self.btn_registrar)

        # Cache de datos
        self.cache_maestra = []
        Clock.schedule_once(self.cargar_datos, 1)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def cargar_datos(self, dt):
        def tarea():
            try:
                res = self.supabase.table("maestra").select("*").execute()
                self.cache_maestra = res.data
            except Exception as e: print(f"Error carga: {e}")
        threading.Thread(target=tarea).start()

    def on_search_change(self, instance, value):
        t = value.upper()
        if not t:
            self.lbl_total.text = "STOCK TOTAL: 0"
            return

        # Búsqueda: Si es número, busca código. Si es texto, busca nombre.
        if t.isdigit():
            match = [i for i in self.cache_maestra if t in str(i['cod_int'])]
        else:
            match = [i for i in self.cache_maestra if t in str(i['nombre']).upper()]

        if match:
            # Sumamos el total de los encontrados
            total = sum(float(m.get('cantidad_total', 0)) for m in match)
            self.lbl_total.text = f"STOCK TOTAL: {int(total)}"
        else:
            self.lbl_total.text = "STOCK TOTAL: 0"

class MegazordApp(App):
    def build(self):
        return MobileMegazord()

if __name__ == '__main__':
    MegazordApp().run()
