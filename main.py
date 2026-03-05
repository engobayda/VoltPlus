import flet as ft
import math
import urllib.request
import json
import threading

def main(page: ft.Page):
    page.title = "VoltPlus - Smart Solar Sizing"
    page.theme_mode = "dark"
    page.bgcolor = "#0f172a" 
    page.window.width = 480
    page.window.height = 850
    page.scroll = "auto"
    page.padding = 20

    title = ft.Text("⚡ التصميم الهندسي الذكي", size=24, weight="bold", color="#38bdf8", text_align="center")

    def CustomInput(label, value, suffix_str=""):
        return ft.TextField(
            label=label, 
            value=str(value), 
            suffix=ft.Text(suffix_str, color="#94a3b8") if suffix_str else None,
            border_color="#334155", 
            focused_border_color="#38bdf8",
            border_radius=8, 
            width=200, 
            height=60, 
            text_align="center"
        )

    day_load_in = CustomInput("حمل النهار الأقصى", 3000, "W")
    day_hours_in = CustomInput("ساعات عمل النهار", 0, "h")
    night_load_in = CustomInput("حمل الليل الأقصى", 2000, "W")
    night_hours_in = CustomInput("ساعات عمل الليل", 0, "h")
    sun_hours_in = CustomInput("ساعات الذروة (PSH)", 0, "h")

    lbl_angle = ft.Text("اضغط على الزر لجلب البيانات الفلكية لموقعك", size=13, color="#94a3b8", weight="bold", text_align="center")

    def get_location_and_astro(e):
        lbl_angle.value = "⏳ جاري الاتصال بالأقمار الصناعية لحساب البيانات..."
        lbl_angle.color = "#fcd34d" 
        page.update()

        def fetch_data():
            try:
                # 1. جلب الموقع باستخدام المكتبة المدمجة urllib
                req_loc = urllib.request.Request('https://ipinfo.io/json', headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_loc, timeout=7) as response:
                    res = json.loads(response.read().decode('utf-8'))
                
                lat, lon = res['loc'].split(',')
                lat, lon = float(lat), float(lon)
                optimal_angle = round(abs(lat))

                # 2. جلب البيانات الفلكية من API
                astro_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0"
                req_astro = urllib.request.Request(astro_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_astro, timeout=7) as response:
                    astro_res = json.loads(response.read().decode('utf-8'))
                
                day_length_sec = astro_res['results']['day_length']
                day_h = round(day_length_sec / 3600, 1)
                night_h = round(24 - day_h, 1)
                psh = round(day_h * 0.45, 1)

                day_hours_in.value = str(day_h)
                night_hours_in.value = str(night_h)
                sun_hours_in.value = str(psh)
                
                lbl_angle.value = f"📍 تم! زاوية: {optimal_angle}° | نهار: {day_h}h | ليل: {night_h}h | PSH: {psh}h"
                lbl_angle.color = "#10b981" 
                
            except Exception as ex:
                lbl_angle.value = "❌ فشل الاتصال. يرجى إدخال الساعات يدوياً."
                lbl_angle.color = "#ef4444"
                print(ex)
            
            page.update()

        threading.Thread(target=fetch_data, daemon=True).start()

    btn_location = ft.ElevatedButton(
        content=ft.Text("🌍 الحساب الفلكي التلقائي (Auto GPS)", size=16, weight="bold", color="white"),
        style=ft.ButtonStyle(
            bgcolor={"": "#0284c7", "hovered": "#0369a1"}, 
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=15
        ),
        width=300,
        on_click=get_location_and_astro
    )

    location_section = ft.Container(
        content=ft.Column([btn_location, lbl_angle], horizontal_alignment="center", spacing=10),
        padding=15, bgcolor="#1e293b", border_radius=12, border=ft.border.all(1, "#334155"), width=page.window.width
    )

    load_section = ft.Container(
        content=ft.Column([
            ft.Text("📊 تحليل الأحمال وساعات التشغيل", color="#e2e8f0", weight="bold"),
            ft.Row([day_load_in, day_hours_in], alignment="spaceBetween"),
            ft.Row([night_load_in, night_hours_in], alignment="spaceBetween"),
        ]),
        padding=15, bgcolor="#1e293b", border_radius=12, border=ft.border.all(1, "#334155")
    )

    sys_eff_slider = ft.Slider(min=50, max=100, divisions=50, value=80, label="{value}%", active_color="#10b981")
    sys_eff_text = ft.Text("كفاءة النظام الشمسي (Losses): 80%", color="#94a3b8", size=12)
    
    def update_eff_text(e):
        sys_eff_text.value = f"كفاءة النظام الشمسي (Losses): {int(e.control.value)}%"
        page.update()
    sys_eff_slider.on_change = update_eff_text

    efficiency_section = ft.Container(
        content=ft.Column([
            ft.Text("☀️ العوامل البيئية والكفاءة", color="#e2e8f0", weight="bold"),
            ft.Row([sun_hours_in], alignment="center"),
            sys_eff_text,
            sys_eff_slider
        ]),
        padding=15, bgcolor="#1e293b", border_radius=12, border=ft.border.all(1, "#334155")
    )

    panel_watt_in = CustomInput("قدرة اللوح الواحد", 615, "W")
    inv_safety_in = CustomInput("عامل أمان الإنفرتر", 25, "%")
    
    bat_volt_in = ft.Dropdown(
        label="فولتية البطاريات", options=[ft.dropdown.Option("12"), ft.dropdown.Option("24"), ft.dropdown.Option("48")],
        value="48", border_color="#334155", border_radius=8, width=200, height=60
    )
    bat_ah_in = CustomInput("سعة البطارية الواحدة", 150, "Ah")
    dod_in = CustomInput("نسبة التفريغ (DoD)", 80, "%") 

    specs_section = ft.Container(
        content=ft.Column([
            ft.Text("⚙️ المواصفات الفنية للمكونات", color="#e2e8f0", weight="bold"),
            ft.Row([panel_watt_in, inv_safety_in], alignment="spaceBetween"),
            ft.Row([bat_volt_in, bat_ah_in], alignment="spaceBetween"),
            ft.Row([dod_in], alignment="center"),
        ]),
        padding=15, bgcolor="#1e293b", border_radius=12, border=ft.border.all(1, "#334155")
    )

    res_inverter = ft.Text("الإنفرتر: ---", size=15, weight="bold", color="#fcd34d")
    res_panels = ft.Text("الألواح: ---", size=15, weight="bold", color="#38bdf8")
    res_battery = ft.Text("البطاريات: ---", size=15, weight="bold", color="#34d399")
    res_energy = ft.Text("الطاقة اليومية: ---", size=13, color="#94a3b8")

    results_section = ft.Container(
        content=ft.Column([
            ft.Text("📈 النتائج الهندسية الدقيقة:", size=18, weight="bold", color="white"),
            ft.Divider(color="#334155"),
            res_inverter, res_panels, res_battery,
            ft.Divider(color="#334155"), res_energy
        ]),
        padding=20, border_radius=12, bgcolor="#111827", border=ft.border.all(1, "#38bdf8")
    )

    def calculate_accurate(e):
        try:
            day_load, day_hours = float(day_load_in.value), float(day_hours_in.value)
            night_load, night_hours = float(night_load_in.value), float(night_hours_in.value)
            sun_hours = float(sun_hours_in.value)
            sys_eff = float(sys_eff_slider.value) / 100
            panel_watt = float(panel_watt_in.value)
            inv_safety = float(inv_safety_in.value) / 100
            bat_volt, bat_ah = float(bat_volt_in.value), float(bat_ah_in.value)
            dod = float(dod_in.value) / 100

            peak_load = max(day_load, night_load)
            inverter_size = peak_load * (1 + inv_safety)

            day_energy = day_load * day_hours
            night_energy = night_load * night_hours
            total_daily_energy = day_energy + night_energy

            required_solar_generation = total_daily_energy / sys_eff
            sun_hours_safe = sun_hours if sun_hours > 0 else 1 
            total_panel_watts = required_solar_generation / sun_hours_safe
            num_panels = math.ceil(total_panel_watts / panel_watt)

            total_battery_energy_needed = night_energy / dod
            total_ah_needed = total_battery_energy_needed / bat_volt
            num_batteries = math.ceil(total_ah_needed / bat_ah)

            res_inverter.value = f"🔌 سعة الإنفرتر المقترحة: {inverter_size:,.0f} واط"
            res_panels.value = f"☀️ مصفوفة الألواح: {num_panels} لوح (قدرة {num_panels * panel_watt:,.0f}W)"
            res_battery.value = f"🔋 عدد البطاريات: {num_batteries} بطارية (بناءً على {bat_volt}V نظام)"
            res_energy.value = f"⚡ إجمالي الاستهلاك اليومي: {total_daily_energy / 1000:,.1f} kWh"

        except ValueError:
            res_inverter.value = "⚠️ يرجى تحديد الموقع أولاً أو إدخال الأرقام يدوياً!"
            res_panels.value, res_battery.value, res_energy.value = "", "", ""

        page.update()

    btn_calc = ft.ElevatedButton(
        content=ft.Text("🚀 إجـراء الحـسـابـات", size=18, weight="bold", color="white"),
        style=ft.ButtonStyle(bgcolor={"": "#10b981", "hovered": "#059669"}, shape=ft.RoundedRectangleBorder(radius=10), padding=15),
        width=page.window.width, on_click=calculate_accurate
    )

    page.add(ft.Column([
        title, ft.Divider(color="transparent", height=5),
        location_section, load_section, efficiency_section, specs_section, btn_calc, results_section
    ], spacing=15, horizontal_alignment="center"))

if __name__ == "__main__":
    ft.app(target=main)
