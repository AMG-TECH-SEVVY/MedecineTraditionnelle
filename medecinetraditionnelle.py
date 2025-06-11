import tkinter as tk
from tkinter import ttk, messagebox, Listbox, MULTIPLE
import psycopg2
from psycopg2 import Error
import configparser

class MedicalDiagnosisInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface de Diagnostic Médical")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variables pour stocker les données
        self.connection = None
        self.resultats_data = []
        self.symptomes_data = []
        self.soins_data = []
        
        # Initialiser la connexion à la base de données
        self.init_database_connection()
        
        # Créer l'interface
        self.create_widgets()       
        # Charger les données initiales
        self.create_widgets()
    
    def init_database_connection(self):
        """Initialise la connexion à la base de données PostgreSQL"""
        try:
            # Configuration de la base de données
            self.connection = psycopg2.connect(
                host="localhost",
                port="5433",
                database="SanteAfricaineDataset",
                user="postgres",
                password="amdy2001"
            )
            print("Connexion à PostgreSQL réussie")
        except Error as e:
            messagebox.showerror("Erreur de connexion", f"Impossible de se connecter à la base de données:\n{e}")
            self.connection = None
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface"""
        # Titre principal
        title_label = tk.Label(self.root, text="Système de Diagnostic Médical", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=10)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Premier cadre : Résultats
        self.create_results_frame(main_frame)
        
        # Deuxième cadre : Symptômes et Soins
        self.create_symptoms_care_frame(main_frame)
        
        # Troisième cadre : Informations Patient
        self.create_patient_info_frame(main_frame)
        
        # Boutons d'action
        self.create_action_buttons(main_frame)

    def create_results_frame(self, parent):
        """Crée le cadre pour les résultats avec requête SQL intégrée"""
        # Création du cadre principal pour les résultats
        results_frame = tk.LabelFrame(parent, text="1. Sélection des Résultats", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#f0f0f0', fg='#2c3e50', padx=10, pady=10)
        results_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame pour le bouton de sélection des résultats
        selection_frame = tk.Frame(results_frame, bg='#f0f0f0')
        selection_frame.pack(fill=tk.X, pady=5)
        
        # Bouton pour afficher tous les résultats disponibles
        # Utilise la requête : SELECT DISTINCT resultat FROM medecine_data WHERE resultat IS NOT NULL
        tk.Button(selection_frame, text="Voir tous les Résultats", 
                 command=self.show_results, bg='#3498db', fg='white',
                 font=('Arial', 10, 'bold'), width=20).pack(side=tk.LEFT)
        
        # Label pour les résultats sélectionnés
        tk.Label(results_frame, text="Résultats sélectionnés:",
                bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        # Listbox pour afficher les résultats sélectionnés par l'utilisateur
        self.selected_results_listbox = Listbox(results_frame, height=4, selectmode=MULTIPLE)
        self.selected_results_listbox.pack(fill=tk.X, pady=(0, 5))

    def create_symptoms_care_frame(self, parent):
        """Crée le cadre pour les symptômes et soins avec requêtes SQL intégrées"""
        # Création du cadre principal pour symptômes et soins
        symptoms_care_frame = tk.LabelFrame(parent, text="2. Symptômes et Soins", 
                                          font=('Arial', 12, 'bold'),
                                          bg='#f0f0f0', fg='#2c3e50', padx=10, pady=10)
        symptoms_care_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame pour les boutons d'action
        buttons_frame = tk.Frame(symptoms_care_frame, bg='#f0f0f0')
        buttons_frame.pack(fill=tk.X, pady=5)
        
        # Bouton pour afficher les symptômes
        # Utilise la requête : SELECT DISTINCT symptomes FROM medecine_data WHERE symptomes IS NOT NULL
        tk.Button(buttons_frame, text="Donner les Symptômes", 
                 command=self.show_symptoms, bg='#e74c3c', fg='white',
                 font=('Arial', 10, 'bold'), width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton pour afficher les soins
        # Utilise la requête : SELECT DISTINCT soins FROM medecine_data WHERE soins IS NOT NULL
        tk.Button(buttons_frame, text="Donner les Soins", 
                 command=self.show_care, bg='#27ae60', fg='white',
                 font=('Arial', 10, 'bold'), width=20).pack(side=tk.LEFT)
        
        # Frame pour organiser les listes côte à côte
        lists_frame = tk.Frame(symptoms_care_frame, bg='#f0f0f0')
        lists_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Colonne pour les symptômes
        symptoms_column = tk.Frame(lists_frame, bg='#f0f0f0')
        symptoms_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(symptoms_column, text="Symptômes sélectionnés:",
                bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.symptoms_listbox = Listbox(symptoms_column, height=8, selectmode=MULTIPLE)
        self.symptoms_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Colonne pour les soins
        care_column = tk.Frame(lists_frame, bg='#f0f0f0')
        care_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(care_column, text="Soins sélectionnés:",
                bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.care_listbox = Listbox(care_column, height=8, selectmode=MULTIPLE)
        self.care_listbox.pack(fill=tk.BOTH, expand=True)
    
    def create_patient_info_frame(self, parent):
        """Crée le cadre pour les informations patient avec boutons pour charger les données"""
        # Création du cadre principal pour les informations patient
        patient_frame = tk.LabelFrame(parent, text="3. Informations Patient", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#f0f0f0', fg='#2c3e50', padx=10, pady=10)
        patient_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame pour les boutons de chargement des données
        load_buttons_frame = tk.Frame(patient_frame, bg='#f0f0f0')
        load_buttons_frame.pack(fill=tk.X, pady=5)
        
        # Bouton pour charger les catégories d'âge depuis la base de données
        tk.Button(load_buttons_frame, text="Catégories Âges", 
                 command=self.load_age_categories, bg='#f39c12', fg='white',
                 font=('Arial', 9, 'bold'), width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        # Bouton pour charger les régions depuis la base de données
        tk.Button(load_buttons_frame, text="Charger Régions", 
                 command=self.load_regions, bg='#8e44ad', fg='white',
                 font=('Arial', 9, 'bold'), width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        # Bouton pour charger les activités depuis la base de données
        tk.Button(load_buttons_frame, text="Charger Activités", 
                 command=self.load_activities, bg='#16a085', fg='white',
                 font=('Arial', 9, 'bold'), width=15).pack(side=tk.LEFT)
        
        # Grid pour organiser les champs de saisie
        info_grid = tk.Frame(patient_frame, bg='#f0f0f0')
        info_grid.pack(fill=tk.X, pady=10)
        
        # Champ Âge
        tk.Label(info_grid, text="Âge:", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.age_entry = tk.Entry(info_grid, width=15)
        self.age_entry.grid(row=0, column=1, padx=(0, 20))
        
        # Champ Sexe
        tk.Label(info_grid, text="Sexe:", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.sex_combobox = ttk.Combobox(info_grid, values=["Masculin", "Féminin"], width=12, state="readonly")
        self.sex_combobox.grid(row=0, column=3, padx=(0, 20))
        
        # Champ Activité (sera peuplé par la base de données)
        tk.Label(info_grid, text="Activité:", bg='#f0f0f0', font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.activity_combobox = ttk.Combobox(info_grid, width=15, state="readonly")
        self.activity_combobox.grid(row=1, column=1, padx=(0, 20), pady=(10, 0))
        
        # Champ Saison
        tk.Label(info_grid, text="Saison:", bg='#f0f0f0', font=('Arial', 10)).grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.season_combobox = ttk.Combobox(info_grid, values=["Printemps", "Été", "Automne", "Hiver"], width=12, state="readonly")
        self.season_combobox.grid(row=1, column=3, padx=(0, 20), pady=(10, 0))
        
        # Champ Région (sera peuplé par la base de données)
        tk.Label(info_grid, text="Région:", bg='#f0f0f0', font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.region_combobox = ttk.Combobox(info_grid, width=30, state="readonly")
        self.region_combobox.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def create_action_buttons(self, parent):
        """Crée les boutons d'action principaux"""
        action_frame = tk.Frame(parent, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, pady=10)
        
        # Bouton d'analyse des données
        tk.Button(action_frame, text="Analyser", command=self.analyze_data,
                 bg='#9b59b6', fg='white', font=('Arial', 12, 'bold'),
                 width=15, height=2).pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton de réinitialisation
        tk.Button(action_frame, text="Réinitialiser", command=self.reset_form,
                 bg='#95a5a6', fg='white', font=('Arial', 12, 'bold'),
                 width=15, height=2).pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton de sauvegarde
        tk.Button(action_frame, text="Sauvegarder", command=self.save_data,
                 bg='#f39c12', fg='white', font=('Arial', 12, 'bold'),
                 width=15, height=2).pack(side=tk.LEFT)
    
    def load_initial_data(self):
        """Charge les données initiales depuis la base de données"""
        if self.connection is None:
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Charger les symptômes depuis la base de données
            # Si une table symptomes existe, l'utiliser, sinon créer des données par défaut
            try:
                cursor.execute("SELECT id, nom_symptome FROM symptomes ORDER BY nom_symptome")
                self.symptomes_data = cursor.fetchall()
            except:
                # Données par défaut si la table n'existe pas
                self.symptomes_data = [(1, "Fièvre"), (2, "Toux"), (3, "Maux de tête"), (4, "Fatigue")]
            
            # Charger les soins depuis la base de données
            try:
                cursor.execute("SELECT id, soins_prescrits FROM soins_prescrits ORDER BY soins_prescrits")
                self.soins_data = cursor.fetchall()
            except:
                # Données par défaut si la table n'existe pas
                self.soins_data = [(1, "Repos"), (2, "Médicaments"), (3, "Physiothérapie"), (4, "Suivi médical")]
            
            cursor.close()
            
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des données:\n{e}")
    
    def show_results(self):
        """Affiche la liste des résultats disponibles depuis la base de données"""
        if self.connection is None:
            messagebox.showwarning("Attention", "Pas de connexion à la base de données")
            return
        
        try:
            cursor = self.connection.cursor()
            # Requête SQL pour récupérer tous les résultats distincts non-nuls
            cursor.execute("SELECT DISTINCT resultat FROM medecine_data WHERE resultat IS NOT NULL ORDER BY resultat")
            results_data = [(i, row[0]) for i, row in enumerate(cursor.fetchall())]
            cursor.close()
            
            if not results_data:
                messagebox.showwarning("Attention", "Aucun résultat disponible dans la base de données")
                return
                
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération des résultats:\n{e}")
            return
        
        # Création de la fenêtre popup pour sélectionner les résultats
        self._create_selection_popup("Résultats", results_data, self.selected_results_listbox)
    
    def show_symptoms(self):
        """Affiche les symptômes disponibles depuis la base de données"""
        if self.connection is None:
            messagebox.showwarning("Attention", "Pas de connexion à la base de données")
            return
        
        try:
            cursor = self.connection.cursor()
            # Requête SQL pour récupérer tous les symptômes distincts non-nuls
            cursor.execute("SELECT DISTINCT symptomes FROM medecine_data WHERE symptomes IS NOT NULL ORDER BY symptomes")
            symptoms_data = [(i, row[0]) for i, row in enumerate(cursor.fetchall())]
            cursor.close()
            
            if not symptoms_data:
                messagebox.showwarning("Attention", "Aucun symptôme disponible dans la base de données")
                return
                
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération des symptômes:\n{e}")
            return
        
        # Création de la fenêtre popup pour sélectionner les symptômes
        self._create_selection_popup("Symptômes", symptoms_data, self.symptoms_listbox)
    
    def show_care(self):
        """Affiche les soins disponibles depuis la base de données"""
        if self.connection is None:
            messagebox.showwarning("Attention", "Pas de connexion à la base de données")
            return
        
        try:
            cursor = self.connection.cursor()
            # Requête SQL pour récupérer tous les soins distincts non-nuls
            cursor.execute("SELECT DISTINCT soins_prescrits FROM medecine_data WHERE soins_prescrits IS NOT NULL ORDER BY soins_prescrits")
            care_data = [(i, row[0]) for i, row in enumerate(cursor.fetchall())]
            cursor.close()
            
            if not care_data:
                messagebox.showwarning("Attention", "Aucun soin disponible dans la base de données")
                return
                
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération des soins:\n{e}")
            return
        
        # Création de la fenêtre popup pour sélectionner les soins
        self._create_selection_popup("Soins", care_data, self.care_listbox)
    
    def load_age_categories(self):
        """Charge et affiche les catégories d'âge depuis la base de données"""
        if self.connection is None:
            messagebox.showwarning("Attention", "Pas de connexion à la base de données")
            return
        
        try:
            cursor = self.connection.cursor()
            # Requête SQL pour analyser les catégories d'âge
            cursor.execute("""
                SELECT DISTINCT age from medecine_data WHERE age IS NOT NULL ORDER BY age"      
            """)
            age_categories = cursor.fetchall()
            cursor.close()
            
            if age_categories:
                # Affichage des statistiques d'âge dans une messagebox
                stats_text = "Catégories d'âge dans la base de données:\n\n"
                for category, count in age_categories:
                    stats_text += f"• {category}: {count} patients\n"
                messagebox.showinfo("Catégories d'Âge", stats_text)
            else:
                messagebox.showwarning("Attention", "Aucune donnée d'âge disponible")
                
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des catégories d'âge:\n{e}")
    
    def load_regions(self):
        """Charge les régions disponibles depuis la base de données"""
        if self.connection is None:
            messagebox.showwarning("Attention", "Pas de connexion à la base de données")
            return
        
        try:
            cursor = self.connection.cursor()
            # Requête SQL pour récupérer toutes les régions distinctes
            cursor.execute("SELECT DISTINCT region FROM medecine_data WHERE region IS NOT NULL ORDER BY region")
            regions = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            if regions:
                # Mise à jour du combobox des régions
                self.region_combobox['values'] = regions
                messagebox.showinfo("Succès", f"{len(regions)} régions chargées avec succès")
            else:
                messagebox.showwarning("Attention", "Aucune région disponible dans la base de données")
                
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des régions:\n{e}")
    
    def load_activities(self):
        """Charge les activités disponibles depuis la base de données"""
        if self.connection is None:
            messagebox.showwarning("Attention", "Pas de connexion à la base de données")
            return
        
        try:
            cursor = self.connection.cursor()
            # Requête SQL pour récupérer toutes les activités distinctes
            cursor.execute("SELECT DISTINCT activite FROM medecine_data WHERE activite IS NOT NULL ORDER BY activite")
            activities = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            if activities:
                # Mise à jour du combobox des activités
                self.activity_combobox['values'] = activities
                messagebox.showinfo("Succès", f"{len(activities)} activités chargées avec succès")
            else:
                messagebox.showwarning("Attention", "Aucune activité disponible dans la base de données")
                
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des activités:\n{e}")
    
    def _create_selection_popup(self, title, data, target_listbox):
        """Crée une fenêtre popup générique pour la sélection d'éléments"""
        # Création de la fenêtre popup
        selection_window = tk.Toplevel(self.root)
        selection_window.title(f"Sélection des {title}")
        selection_window.geometry("500x400")
        selection_window.configure(bg='#f0f0f0')
        selection_window.grab_set()  # Rendre la fenêtre modale
        
        # Label de titre
        tk.Label(selection_window, text=f"Sélectionnez les {title.lower()} souhaités:",
                bg='#f0f0f0', font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Frame pour la liste avec scrollbar
        list_frame = tk.Frame(selection_window, bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Listbox avec scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        selection_listbox = Listbox(list_frame, selectmode=MULTIPLE, yscrollcommand=scrollbar.set)
        selection_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=selection_listbox.yview)
        
        # Remplir la listbox avec les données
        for item in data:
            selection_listbox.insert(tk.END, item[1])
        
        # Frame pour les boutons
        button_frame = tk.Frame(selection_window, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        # Fonction de confirmation de sélection
        def confirm_selection():
            selected_indices = selection_listbox.curselection()
            target_listbox.delete(0, tk.END)  # Vider la liste actuelle
            
            # Ajouter les éléments sélectionnés
            for index in selected_indices:
                target_listbox.insert(tk.END, data[index][1])
            
            selection_window.destroy()
        
        # Boutons d'action
        tk.Button(button_frame, text="Tout sélectionner", 
                 command=lambda: selection_listbox.select_set(0, tk.END),
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="Tout désélectionner", 
                 command=lambda: selection_listbox.selection_clear(0, tk.END),
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="Confirmer", command=confirm_selection,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="Annuler", command=selection_window.destroy,
                 bg='#95a5a6', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    
    def analyze_data(self):
        """Analyse les données saisies et effectue des requêtes de validation"""
        # Récupération de toutes les données saisies
        selected_results = [self.selected_results_listbox.get(i) for i in range(self.selected_results_listbox.size())]
        selected_symptoms = [self.symptoms_listbox.get(i) for i in range(self.symptoms_listbox.size())]
        selected_care = [self.care_listbox.get(i) for i in range(self.care_listbox.size())]
        
        patient_info = {
            'age': self.age_entry.get(),
            'sexe': self.sex_combobox.get(),
            'activite': self.activity_combobox.get(),
            'saison': self.season_combobox.get(),
            'region': self.region_combobox.get()
        }
        
        # Validation des données obligatoires
        if not selected_results:
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins un résultat")
            return
        
        if not patient_info['age'] or not patient_info['sexe']:
            messagebox.showwarning("Attention", "Veuillez renseigner l'âge et le sexe du patient")
            return
        
        # Recherche de cas similaires dans la base de données
        similar_cases = self._find_similar_cases(patient_info, selected_symptoms, selected_results)
        
        # Préparation du texte d'analyse
        analysis_text = f"""ANALYSE DIAGNOSTIQUE DÉTAILLÉE

=== DONNÉES PATIENT ===
• Âge: {patient_info['age']} ans
• Sexe: {patient_info['sexe']}
• Activité: {patient_info['activite'] if patient_info['activite'] else 'Non spécifiée'}
• Saison: {patient_info['saison'] if patient_info['saison'] else 'Non spécifiée'}
• Région: {patient_info['region'] if patient_info['region'] else 'Non spécifiée'}

=== RÉSULTATS SÉLECTIONNÉS ===
{chr(10).join([f"• {result}" for result in selected_results])}

=== SYMPTÔMES IDENTIFIÉS ===
{chr(10).join([f"• {symptom}" for symptom in selected_symptoms]) if selected_symptoms else '• Aucun symptôme spécifié'}

=== SOINS RECOMMANDÉS ===
{chr(10).join([f"• {care}" for care in selected_care]) if selected_care else '• Aucun soin spécifié'}

=== ANALYSE COMPARATIVE ===
{similar_cases}
        """
        
        # Affichage du résultat de l'analyse
        messagebox.showinfo("Résultat de l'Analyse Diagnostique", analysis_text)  
    def save_data(self):
        """Sauvegarde les données dans la base de données avec toutes les informations"""
        if self.connection is None:
            messagebox.showerror("Erreur", "Pas de connexion à la base de données")
            return
        
        try:
        
            
            # Récupération des données sélectionnées
            selected_results = [self.selected_results_listbox.get(i) for i in range(self.selected_results_listbox.size())]
            selected_symptoms = [self.symptoms_listbox.get(i) for i in range(self.symptoms_listbox.size())]
            selected_care = [self.care_listbox.get(i) for i in range(self.care_listbox.size())]
            
            # Préparation des données pour l'insertion
            patient_data = (
                int(self.age_entry.get()) if self.age_entry.get().isdigit() else None,
                self.sex_combobox.get() if self.sex_combobox.get() else None,
                self.activity_combobox.get() if self.activity_combobox.get() else None,
                self.season_combobox.get() if self.season_combobox.get() else None,
                self.region_combobox.get() if self.region_combobox.get() else None,
                selected_results,
                selected_symptoms,
                selected_care,
                f"Consultation patient - Résultats: {len(selected_results)}, Symptômes: {len(selected_symptoms)}, Soins: {len(selected_care)}"
            )
            
            # Requête d'insertion
            insert_query = """
                INSERT INTO consultations 
                (age, sexe, activite, saison, region, resultats_selectionnes, 
                 symptomes_selectionnes, soins_selectionnes, notes) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
        except Error as e:
            self.connection.rollback()
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
        except ValueError as e:
            messagebox.showerror("Erreur", f"Erreur de validation des données:\n{e}")
    
    def reset_form(self):
        """Réinitialise tous les champs du formulaire"""
        # Vider toutes les listbox de sélection
        self.selected_results_listbox.delete(0, tk.END)
        self.symptoms_listbox.delete(0, tk.END)
        self.care_listbox.delete(0, tk.END)
        
        # Vider tous les champs de saisie
        self.age_entry.delete(0, tk.END)
        self.sex_combobox.set('')
        self.activity_combobox.set('')
        self.season_combobox.set('')
        self.region_combobox.set('')
        
        # Message de confirmation
        messagebox.showinfo("Réinitialisation", "Formulaire réinitialisé avec succès")
    
    def get_database_statistics(self):
        """Récupère et affiche les statistiques de la base de données"""
        if self.connection is None:
            messagebox.showwarning("Attention", "Pas de connexion à la base de données")
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Statistiques générales de la table medecine_data
            stats_queries = {
                "Total des enregistrements": "SELECT COUNT(*) FROM medecine_data",
                "Nombre de résultats uniques": "SELECT COUNT(DISTINCT resultat) FROM medecine_data WHERE resultat IS NOT NULL",
                "Nombre de symptômes uniques": "SELECT COUNT(DISTINCT symptomes) FROM medecine_data WHERE symptomes IS NOT NULL",
                "Nombre de soins uniques": "SELECT COUNT(DISTINCT soins) FROM medecine_data WHERE soins IS NOT NULL",
                "Nombre de régions": "SELECT COUNT(DISTINCT region) FROM medecine_data WHERE region IS NOT NULL",
                "Âge moyen": "SELECT AVG(age) FROM medecine_data WHERE age IS NOT NULL"
            }
            
            stats_text = "=== STATISTIQUES DE LA BASE DE DONNÉES ===\n\n"
            
            for description, query in stats_queries.items():
                cursor.execute(query)
                result = cursor.fetchone()[0]
                if description == "Âge moyen":
                    stats_text += f"• {description}: {result:.1f} ans\n"
                else:
                    stats_text += f"• {description}: {result}\n"
            
            # Répartition par sexe
            cursor.execute("SELECT sexe, COUNT(*) FROM medecine_data WHERE sexe IS NOT NULL GROUP BY sexe")
            gender_stats = cursor.fetchall()
            if gender_stats:
                stats_text += "\n=== RÉPARTITION PAR SEXE ===\n"
                for gender, count in gender_stats:
                    stats_text += f"• {gender}: {count} cas\n"
            
            cursor.close()
            messagebox.showinfo("Statistiques Base de Données", stats_text)
            
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération des statistiques:\n{e}")
    
    def search_patient_data(self):
        """Recherche des données patients selon des critères spécifiques"""
        if self.connection is None:
            messagebox.showwarning("Attention", "Pas de connexion à la base de données")
            return
        
        # Fenêtre de recherche
        search_window = tk.Toplevel(self.root)
        search_window.title("Recherche de Patients")
        search_window.geometry("600x400")
        search_window.configure(bg='#f0f0f0')
        search_window.grab_set()
        
        # Titre
        tk.Label(search_window, text="Recherche Avancée de Patients", 
                font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=10)
        
        # Frame pour les critères de recherche
        criteria_frame = tk.LabelFrame(search_window, text="Critères de recherche", 
                                      font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        criteria_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Champs de recherche
        tk.Label(criteria_frame, text="Âge minimum:", bg='#f0f0f0').grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        age_min_entry = tk.Entry(criteria_frame, width=15)
        age_min_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(criteria_frame, text="Âge maximum:", bg='#f0f0f0').grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        age_max_entry = tk.Entry(criteria_frame, width=15)
        age_max_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(criteria_frame, text="Sexe:", bg='#f0f0f0').grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        search_sex_combo = ttk.Combobox(criteria_frame, values=["", "Masculin", "Féminin"], width=12, state="readonly")
        search_sex_combo.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(criteria_frame, text="Région:", bg='#f0f0f0').grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        search_region_entry = tk.Entry(criteria_frame, width=20)
        search_region_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Zone de résultats
        results_frame = tk.LabelFrame(search_window, text="Résultats de recherche", 
                                     font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Text widget pour afficher les résultats
        results_text = tk.Text(results_frame, height=10, width=70)
        scrollbar_results = tk.Scrollbar(results_frame, command=results_text.yview)
        results_text.config(yscrollcommand=scrollbar_results.set)
        results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_results.pack(side=tk.RIGHT, fill=tk.Y)
        
        def perform_search():
            """Exécute la recherche selon les critères saisis"""
            try:
                cursor = self.connection.cursor()
                
                # Construction de la requête dynamique
                base_query = "SELECT age, sexe, region, activite, resultat, symptomes FROM medecine_data WHERE 1=1"
                params = []
                
                # Ajout des conditions selon les critères
                if age_min_entry.get():
                    base_query += " AND age >= %s"
                    params.append(int(age_min_entry.get()))
                
                if age_max_entry.get():
                    base_query += " AND age <= %s"
                    params.append(int(age_max_entry.get()))
                
                if search_sex_combo.get():
                    base_query += " AND sexe = %s"
                    params.append(search_sex_combo.get())
                
                if search_region_entry.get():
                    base_query += " AND region ILIKE %s"
                    params.append(f"%{search_region_entry.get()}%")
                
                base_query += " ORDER BY age, sexe LIMIT 50"
                
                cursor.execute(base_query, params)
                search_results = cursor.fetchall()
                
                # Affichage des résultats
                results_text.delete(1.0, tk.END)
                if search_results:
                    results_text.insert(tk.END, f"=== {len(search_results)} RÉSULTATS TROUVÉS ===\n\n")
                    for i, row in enumerate(search_results, 1):
                        age, sexe, region, activite, resultat, symptomes = row
                        results_text.insert(tk.END, f"{i}. Patient {sexe}, {age} ans\n")
                        results_text.insert(tk.END, f"   Région: {region or 'Non spécifiée'}\n")
                        results_text.insert(tk.END, f"   Activité: {activite or 'Non spécifiée'}\n")
                        results_text.insert(tk.END, f"   Résultat: {resultat or 'Non spécifié'}\n")
                        results_text.insert(tk.END, f"   Symptômes: {symptomes or 'Non spécifiés'}\n")
                        results_text.insert(tk.END, "-" * 50 + "\n")
                else:
                    results_text.insert(tk.END, "Aucun résultat trouvé pour ces critères")
                
                cursor.close()
                
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la recherche:\n{e}")
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez vérifier le format des âges (nombres entiers)")
        
        # Boutons d'action
        button_frame = tk.Frame(search_window, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Rechercher", command=perform_search,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Fermer", command=search_window.destroy,
                 bg='#95a5a6', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
    
    def __del__(self):
        """Ferme proprement la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            print("Connexion à la base de données fermée")

def main():
    """Fonction principale pour lancer l'application"""
    # Décommenter pour voir le schéma de base de données
    # create_database_schema()
    
    # Création et lancement de l'interface
    root = tk.Tk()
    app = MedicalDiagnosisInterface(root)
    
    # Menu additionnel pour les fonctionnalités avancées
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # Menu Base de données
    db_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Base de données", menu=db_menu)
    db_menu.add_command(label="Statistiques", command=app.get_database_statistics)
    db_menu.add_command(label="Recherche avancée", command=app.search_patient_data)
    db_menu.add_separator()
    
    # Menu Aide
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Aide", menu=help_menu)
    help_menu.add_command(label="À propos", 
                         command=lambda: messagebox.showinfo("À propos", 
                                                            "Interface de Diagnostic Médical v2.0\n\n"
                                                            "Système de gestion des diagnostics médicaux\n"
                                                            "avec connexion PostgreSQL\n\n"
                                                            "Fonctionnalités:\n"
                                                            "• Sélection de résultats, symptômes et soins\n"
                                                            "• Analyse comparative des cas\n"
                                                            "• Sauvegarde en base de données\n"
                                                            "• Recherche avancée de patients\n"
                                                            "• Statistiques détaillées"))
    
    # Lancement de l'application
    root.mainloop()

if __name__ == "__main__":
    main()