from datetime import datetime

from django.contrib import messages
from django.shortcuts import render

# Create your views here.
import cx_Oracle
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from magazin_dulciuri.connect import connect_to_oracle
from magazin_dulciuri.forms import ProdusForm, AprovizionareForm, EditareProdusForm

# Variabila globala ca sa determin ce produs trebuie editat
produs_de_editat = None #nu mai este nevoie de ea

connection = connect_to_oracle()

# Manageriez pagina de login
def autentificare_magazin(request):
    # varianta primitiva -> incarcare pagina
    # template = loader.get_template('registration/autentificare.html')
    # return HttpResponse(template.render())

    if request.method == 'POST':
        nume_utilizator = request.POST['nume_utilizator']
        parola = request.POST['parola']
        nume_util = "'" + nume_utilizator + "'"
        prl = "'" + parola + "'"

        # Interoghez baza de date pentru a verifica dacă utilizatorul există
        #connection = connect_to_oracle()
        cursor = connection.cursor()
        cursor.execute('SELECT  * FROM CLIENTI WHERE nume_utilizator = ' + nume_util + ' and parola = ' + prl)
        #cursor.execute("SELECT * FROM CLIENTI WHERE nume_utilizator = :nume_utilizator AND parola = :parola",
                       #nume_utilizator=nume_utilizator, parola=parola)
        client = cursor.fetchone()

        # Dacă utilizatorul există, se conecteaza și este redirecționat către pagina de pornire
        if client:
            return redirect('acasa')
        # În caz contrar, se afiseaza pe pagina de autentificare un mesaj de eroare
        else:
            return render(request, 'registration/autentificare.html',
                          {'errors': 'Nume de utilizator sau parola invalida.'})
    else:
        return render(request, 'registration/autentificare.html')


# Manageriez pagina de inregistrare
def inregistrare_magazin(request):
    #connection = connect_to_oracle()
    if request.method == 'POST':
        cursor = connection.cursor()
        email_client = request.POST['email']
        email = "'" + email_client + "'"
        cursor.execute("SELECT email_client FROM DETALII_CLIENT WHERE email_client = " + email )
        #cursor.execute("SELECT email_client FROM DETALII_CLIENT WHERE email_client = :email_client", {'email_client': email_client})
        email_existent = cursor.fetchone()
        if email_existent:
            messages.error(request, 'Email deja exista!')
            return render(request, 'registration/inregistrare.html')
        else:
            nume_client = request.POST['nume'] + " " + request.POST['prenume']
            email = request.POST['email']
            adresa = request.POST['strada'] + " " + request.POST['numar'] + " " + request.POST['oras']
            telefon = request.POST['telefon']
            nume_utilizator = request.POST['nume_utilizator']
            parola = request.POST['parola']
            tip_utilizator = 'Utilizator'
            cod = "707505"

            print("nume_client", nume_client)
            print("email", email)
            print("Adresa", adresa)
            print("telefon", telefon)
            print("nume_utilizator", nume_utilizator)
            print("parola", parola)
            print("tip_utilizator", tip_utilizator)

            # Introduc o înregistrare în tabelul „CLIENTI” și obțin ID-ul rândului inserat
            id_iesire = cursor.var(cx_Oracle.NUMBER)

            cursor.execute(
                "INSERT INTO CLIENTI (nume_client, nume_utilizator, parola, tip_utilizator) VALUES (:1, :2, :3, :4) RETURNING id_client INTO :5",
                (nume_client, nume_utilizator, parola, tip_utilizator, id_iesire))

            # Inserez o înregistrare în tabelul „DETALII_CLIENT” și utilizez ID-ul rândului inserat în tabelul „CLIENT” ca
            #foreign key
            cursor.execute(
                "INSERT INTO DETALII_CLIENT (id_client, cod_postal, adresa_client, email_client, numar_telefon) VALUES (:1, :2, :3, :4, :5)",
                (id_iesire.getvalue()[0], cod, adresa, email, telefon))

            # Comite tranzactia
            cursor.execute("COMMIT")

            # Inchidere cursor
            cursor.close()
            return redirect('autentificare_magazin')

        # Dacă cererea nu este o solicitare POST, redau șablonul de registru
    else:
        return render(request, 'registration/inregistrare.html')


# Manageriez pagina de acasa
def acasa(request):
    #connection = connect_to_oracle()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM PRODUSE ORDER BY id_produs")

    produse = cursor.fetchall()
    template = loader.get_template('acasa.html')
    context = {'produse': produse}  # dictionar cheie:valoare
    return HttpResponse(template.render(context))


# Manageriez pagina de comenzi
def comenzi(request):
    #connection = connect_to_oracle()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT c.id_comanda, c.pret_comanda, c.data_comanda, cl.nume_client, b.tip_cadou FROM comenzi c, clienti cl, bonusuri b WHERE c.id_client = cl.id_client AND c.id_bonus = b.id_bonus")

    comenzi = cursor.fetchall()
    template = loader.get_template('comenzi.html')
    context = {'comenzi': comenzi}  # dictionar cheie:valoare
    return HttpResponse(template.render(context))


# Manageriez pagina de clienti
def clienti(request):
    #connection = connect_to_oracle()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT cl.id_client, cl.nume_client, cl.nume_utilizator, cl.parola, cl.tip_utilizator, dc.numar_telefon, dc.email_client, dc.adresa_client, dc.cod_postal FROM clienti cl, detalii_client dc WHERE cl.id_client = dc.id_client ")

    clienti = cursor.fetchall()
    # print(clienti)
    template = loader.get_template('clienti.html')
    context = {'clienti': clienti}  # dictionar cheie:valoare
    return HttpResponse(template.render(context))


# Manageriez pagina de aprovizionari
def aprovizionari(request):
    #connection = connect_to_oracle()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT a.cantitate_aprovizionare, a.pret_aprovizionare, a.data_aprovizionare, p.nume_produs FROM aprovizionari a, produse p WHERE p.id_produs = a.id_produs")

    aprovizionari = cursor.fetchall()
    template = loader.get_template('aprovizionari.html')
    context = {'aprovizionari': aprovizionari}  # dictionar cheie:valoare
    return HttpResponse(template.render(context))


# Manageriez pagina de venituri
def venituri(request):
    #connection = connect_to_oracle()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM VENITURI")
    venituri = cursor.fetchall()

    # Determin cel mai fidel client
    cursor.execute(
        "WITH comanda as (SELECT nume_client name, count(comenzi.id_comanda) c_cnt FROM comenzi, clienti WHERE comenzi.id_client = clienti.id_client group by nume_client),maxim as (SELECT max(c_cnt) numar FROM comanda)SELECT name FROM comanda, maxim WHERE c_cnt = numar")
    client_fidel = cursor.fetchone()[0]

    # Determin cel mai cumparat produs
    cursor.execute(
        "WITH produs as (SELECT nume_produs name, count(detalii_comanda.id_produs) p_cnt FROM detalii_comanda, produse WHERE produse.id_produs = detalii_comanda.id_produs group by nume_produs),maxim as (SELECT max(p_cnt) numar FROM produs)SELECT name FROM produs, maxim WHERE p_cnt = numar")
    produs_cumprat = cursor.fetchone()[0]

    # Determin produsul dat spre vanzare in cantitatea cea mai mare
    cursor.execute(
        "SELECT nume_produs FROM produse WHERE id_produs = (SELECT id_produs FROM aprovizionari WHERE cantitate_aprovizionare = (SELECT max(cantitate_aprovizionare) FROM aprovizionari ))")
    produs_vanzare_cant_mare = cursor.fetchone()[0]

    # Determin numele clientului care a primit ca bonus tort
    cursor.execute(
        "SELECT nume_client FROM clienti, bonusuri, comenzi WHERE clienti.id_client = comenzi.id_client AND comenzi.id_bonus = bonusuri.id_bonus AND tip_cadou = 'Tort'")
    bonus_tort = cursor.fetchall()

    # Determin clientii care stau la bloc
    cursor.execute(
        "SELECT nume_client FROM clienti, detalii_client WHERE clienti.id_client = detalii_client.id_client AND adresa_client like '%Bl%'")
    clienti_bloc = cursor.fetchall()

    # Determin numarul de produse care au pretul in intervalul 0, 50 si numarul de produse care au pretul in intervalul 51, 100
    #cursor.execute(
        #"WITH interval1 AS ( SELECT count(id_produs) AS i1 FROM produse WHERE (pret_produs BETWEEN 0 AND 50) ), interval2 AS ( SELECT count(id_produs) AS i2 FROM produse WHERE (pret_produs BETWEEN 51 AND 100) )SELECT i1 AS "(0-50]", i2 AS "[51-100]" FROM interval1, interval2")
    #produse_interval = cursor.fetchall()

    template = loader.get_template('venituri.html')
    context = {'venituri': venituri, 'client_fidel': client_fidel, 'produs_cumparat': produs_cumprat, 'produs_vanzare_cant_mare': produs_vanzare_cant_mare, 'bonus_tort': bonus_tort, 'clienti_bloc': clienti_bloc}  # dictionar cheie:valoare
    return HttpResponse(template.render(context))


# Manageriez pagina de adaugare produs
def adaugare_produs(request):
    print(ProdusForm)
    #connection = connect_to_oracle()

    if request.method == 'POST':
        print("Am intrat aici")
        form = ProdusForm(request.POST)
        if form.is_valid():
            # Conectare la baza de date
            cursor = connection.cursor()

            # Salvez produsul in baza de date
            nume_produs = form.cleaned_data['nume_produs'].lower().capitalize()
            print("nume_produs", nume_produs)
            nume_p = "'" + nume_produs.lower().capitalize() + "'"
            cursor.execute("SELECT * FROM PRODUSE WHERE nume_produs =  %s" % nume_p)
            produs_gasit = cursor.fetchone()
            print("produs_gasit", produs_gasit)
            # Verific daca produsul introdus exista deja
            if produs_gasit == None:
                pret_produs = form.cleaned_data['pret_produs']
                cantitate_disponibila = form.cleaned_data['cantitate_disponibila']
                #cantitate_disponibila = 5

                print("pret_produs", pret_produs)
                #print(cantitate_disponibila)
                # Inserez produsul in tabela PRODUSE
                #numProd = "'" + nume_produs + "'"
                #cursor.execute(
                    #'INSERT INTO PRODUSE(nume_produs, pret_produs, cantitate_disponibila) values (' + numProd + ',' + str(
                     #   pret_produs) + ',' + str(cantitate_disponibila) + ')')

                #cursor.execute(
                   # "INSERT INTO PRODUSE (nume_produs, pret_produs, cantitate_disponibila) VALUES (:1, :2, :3)",
                    #(nume_produs, pret_produs, cantitate_disponibila))
                cursor.execute(
                    "INSERT INTO PRODUSE(nume_produs, pret_produs, cantitate_disponibila) values (:nume_produs, :pret_produs, :cantitate_disponibila)",
                    {'nume_produs': nume_produs, 'pret_produs': pret_produs,
                     'cantitate_disponibila': cantitate_disponibila})

                # Comite tranzactia
                cursor.execute("COMMIT")

                # Inchidere cursor
                cursor.close()
                return redirect('acasa')
            else:
                form = ProdusForm()
                return render(request, 'adaugare_produs.html', {'errors': 'Produsul deja exista.'})
    else:
        form = ProdusForm()
        return render(request, 'adaugare_produs.html', {'form': form})


def adaugare_aprovizionare(request, id_produs):
    #connection = connect_to_oracle()
    # Conectare la baza de date
    cursor = connection.cursor()

    cursor.execute("SELECT nume_produs FROM PRODUSE WHERE id_produs = %s" % id_produs)
    nume_produs = cursor.fetchone()
    if request.method == 'POST':
        form = AprovizionareForm(request.POST)
        if form.is_valid():

            # Salvez aprovizionarea in baza de date
            data_aprovizionare = form.cleaned_data['data_aprovizionare']
            pret_aprovizionare = form.cleaned_data['pret_aprovizionare']
            cantitate_aprovizionare = form.cleaned_data['cantitate_aprovizionare']
            cursor.execute(
                "INSERT INTO APROVIZIONARI(id_produs, pret_aprovizionare, cantitate_aprovizionare ) VALUES(:id_produs, :pret_aprovizionare, :cantitate_aprovizionare)",
                {'id_produs': 13, 'pret_aprovizionare': pret_aprovizionare,
                 'cantitate_aprovizionare': cantitate_aprovizionare})

            # Comite tranzactia
            cursor.execute("COMMIT")

            # Inchidere cursor
            cursor.close()
            return redirect('acasa')
    else:
            form = AprovizionareForm()

    return render(request, 'adaugare_aprovizionare.html', {'form': form, 'nume_produs': nume_produs})


@csrf_exempt
def stergere_produs(request, id_produs):
    #connection = connect_to_oracle()

    # print(id_produs)

    if request.method == 'POST':
        cursor = connection.cursor()
        cursor.execute("DELETE FROM APROVIZIONARI WHERE id_produs = :id_produs", {'id_produs': id_produs})
        cursor.execute("DELETE FROM DETALII_COMANDA WHERE id_produs = :id_produs", {'id_produs': id_produs})
        cursor.execute("DELETE FROM PRODUSE WHERE id_produs = :id_produs", {'id_produs': id_produs})

        # Comite tranzactia
        cursor.execute("COMMIT")

        # Inchidere cursor
        cursor.close()
        return redirect('acasa')

def editare_produs(request, id_produs):
    # Retrieve the product from the database
    #connection = connect_to_oracle()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM PRODUSE WHERE id_produs = :id", {'id': id_produs})

    cursor.execute("SELECT cantitate_disponibila FROM PRODUSE WHERE id_produs = :id", {'id': id_produs})
    cantitate_disponibila = cursor.fetchone()[0]

    cursor.execute("SELECT pret_produs FROM PRODUSE WHERE id_produs = :id", {'id': id_produs})
    pret_produs_vechi = cursor.fetchone()[0]

    cursor.execute("SELECT nume_produs FROM PRODUSE WHERE id_produs = :id", {'id': id_produs})
    nume_produs_vechi = cursor.fetchone()[0]

    if request.method == 'POST':
        form = EditareProdusForm(request.POST)
        if form.is_valid():
            # Alegere solicitată pentru nume, preț
            nume_produs = "'" + form.cleaned_data['nume_produs'] + "'"
            pret_produs = form.cleaned_data['pret_produs']

            cursor.execute("UPDATE PRODUSE\
                            SET pret_produs = %s, nume_produs = %s  WHERE id_produs = %s" \
                           % (pret_produs, nume_produs, id_produs))
            # Comite tranzactia
            cursor.execute("COMMIT")

            # Inchidere cursor
            cursor.close()
            return redirect('acasa')
    else:
        # Render the edit form
        form = EditareProdusForm(initial={'pret_produs': pret_produs_vechi, 'nume_produs': nume_produs_vechi, 'cantitate_disponibila': cantitate_disponibila})

    return render(request, 'editare_produs.html', {'form': form, 'pret_produs': pret_produs_vechi, 'nume_produs': nume_produs_vechi, 'cantitate_disponibila': cantitate_disponibila})
