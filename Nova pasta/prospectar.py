import requests
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, StringVar, OptionMenu
import pandas as pd
import threading
import folium

API_KEY = 'AIzaSyARe82Ghcu-eA6mGq4JGUUjw41j-lYWqm8'  # Sua chave de API

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Prospectar Clientes")
        self.root.geometry("800x700")
        self.root.configure(bg="#e0f7fa")

        # Título
        title = tk.Label(root, text="Prospectar Clientes", font=("Arial", 24, "bold"), bg="#e0f7fa")
        title.pack(pady=20)

        # Entrada da Cidade
        self.city_entry = tk.Entry(root, font=("Arial", 16), width=20)
        self.city_entry.pack(pady=10)
        self.city_entry.insert(0, "Digite a cidade...")

        # Palavra-Chave
        self.keyword_entry = tk.Entry(root, font=("Arial", 16), width=20)
        self.keyword_entry.pack(pady=10)
        self.keyword_entry.insert(0, "Digite uma palavra-chave...")

        # Seleção de Categoria
        self.category_var = StringVar(root)
        self.category_var.set("Categoria")  # Valor padrão
        categories = ["", "Restaurantes", "Lojas", "Serviços", "Escolas"]
        category_menu = OptionMenu(root, self.category_var, *categories)
        category_menu.config(font=("Arial", 16), width=15)
        category_menu.pack(pady=10)

        # Botões
        search_button = tk.Button(root, text="Buscar Clientes", command=self.buscar_clientes, font=("Arial", 16), bg="#4CAF50", fg="white")
        search_button.pack(pady=10)

        save_button = tk.Button(root, text="Salvar Resultados", command=self.salvar_resultados, font=("Arial", 16), bg="#2196F3", fg="white")
        save_button.pack(pady=10)

        # Área de Resultados
        self.results_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12), width=80, height=20)
        self.results_text.pack(pady=10)

        self.resultados = []

    def buscar_clientes(self):
        cidade = self.city_entry.get()
        categoria = self.category_var.get()
        palavra_chave = self.keyword_entry.get()

        if not cidade.strip():
            messagebox.showwarning("Atenção", "Por favor, insira uma cidade.")
            return

        self.results_text.delete(1.0, tk.END)
        self.resultados = []  # Limpa resultados anteriores
        loading_label = tk.Label(self.root, text="Carregando...", font=("Arial", 16), bg="#e0f7fa")
        loading_label.pack(pady=10)

        # Inicia a busca em uma thread separada
        threading.Thread(target=self.realizar_busca, args=(cidade, categoria, palavra_chave, loading_label)).start()

    def realizar_busca(self, cidade, categoria, palavra_chave, loading_label):
        try:
            query = f"empresas+em+{cidade}"
            if categoria:
                query += f"+{categoria.lower()}"
            if palavra_chave:
                query += f"+{palavra_chave.lower()}"

            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()  # Lança um erro para respostas não 200
            results = response.json().get('results', [])

            if not results:
                self.results_text.insert(tk.END, "Nenhum resultado encontrado.")
                return

            for lugar in results:
                nome = lugar.get('name')
                endereco = lugar.get('formatted_address')
                details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={lugar.get('place_id')}&key={API_KEY}"
                details_response = requests.get(details_url)
                details_response.raise_for_status()
                details = details_response.json().get('result', {})
                telefone = details.get('formatted_phone_number', 'Não disponível')

                self.results_text.insert(tk.END, f"Nome: {nome}, Endereço: {endereco}, Telefone: {telefone}\n")
                self.resultados.append({'Nome': nome, 'Endereço': endereco, 'Telefone': telefone})

            # Mostrar Mapa
            self.mostrar_mapa(results)

        except requests.exceptions.HTTPError as err:
            messagebox.showerror("Erro HTTP", f"Ocorreu um erro: {err}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Ocorreu um erro: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")
        finally:
            loading_label.destroy()  # Remove o label de carregamento

    def mostrar_mapa(self, results):
        m = folium.Map(location=[-3.7172, -38.5433], zoom_start=12)  # Coordenadas aproximadas de Fortaleza-CE
        for lugar in results:
            nome = lugar.get('name')
            endereco = lugar.get('formatted_address')
            lat = lugar.get('geometry', {}).get('location', {}).get('lat')
            lng = lugar.get('geometry', {}).get('location', {}).get('lng')
            folium.Marker([lat, lng], popup=f"{nome}<br>{endereco}").add_to(m)

        # Salvar o mapa em um arquivo HTML
        m.save('mapa_resultados.html')
        messagebox.showinfo("Mapa Criado", "O mapa foi salvo como 'mapa_resultados.html'.")

    def salvar_resultados(self):
        if not self.resultados:
            messagebox.showwarning("Atenção", "Nenhum resultado para salvar.")
            return

        arquivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if arquivo:
            if arquivo.endswith('.csv'):
                df = pd.DataFrame(self.resultados)
                df.to_csv(arquivo, index=False)
            elif arquivo.endswith('.xlsx'):
                df = pd.DataFrame(self.resultados)
                df.to_excel(arquivo, index=False)
            messagebox.showinfo("Sucesso", "Resultados salvos com sucesso!")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
