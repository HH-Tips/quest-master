(define (domain spiderman-mysterio-studio) ; Definizione del dominio per la missione di Spider-Man contro Mysterio
  (:requirements :strips :typing :negative-preconditions) ; Requisiti PDDL necessari per la gestione di tipi e precondizioni negative
  (:types ; Dichiarazione dei tipi di entita presenti nel dominio
    location ; Luoghi esplorabili all'interno dello studio cinematografico
    item ; Oggetti fisici raccoglibili come chiavi e gadget
    character ; Entita animate nel dominio
    drone ; Unita di sorveglianza e proiezione ostili
    device ; Macchinari e congegni tecnologici interagibili
    hero villain - character ; Sottotipi per distinguere Spider-Man dall'antagonista Mysterio
  ) ; Chiusura della sezione tipi

  (:predicates ; Dichiarazione dei predicati per tracciare lo stato del mondo
    (hero-at ?h - hero ?l - location) ; Indica che l'eroe si trova in uno specifico luogo
    (villain-at ?v - villain ?l - location) ; Indica che il villain si trova in uno specifico luogo
    (drone-at ?d - drone ?l - location) ; Indica la posizione corrente di un drone proiettore
    (device-at ?dev - device ?l - location) ; Indica che un macchinario e installato in una determinata stanza
    (item-at ?i - item ?l - location) ; Indica che un oggetto si trova a terra in un luogo
    (holding ?h - hero ?i - item) ; Indica che l'eroe possiede uno specifico oggetto nel proprio inventario
    (connected ?from - location ?to - location) ; Definisce un passaggio fisico percorribile tra due stanze
    (blocked-by-drone ?from - location ?to - location ?d - drone) ; Indica che il passaggio tra due aree e sbarrato da un drone
    (door-locked ?from - location ?to - location) ; Indica che la porta tra due stanze e bloccata elettronicamente
    (barrier-active) ; Indica che la barriera olografica difensiva di Mysterio e attiva
    (helmet-blinded ?v - villain) ; Indica che i sensori del casco di Mysterio sono stati accecati dalle ragnatele
    (defeated ?v - villain) ; Indica che Mysterio e stato sconfitto e incapacitato
    (gas-deactivated ?dev - device) ; Indica che il generatore di gas allucinogeno e stato spento
  ) ; Chiusura della sezione predicati

  (:action move ; Azione per permettere all'eroe di spostarsi tra due stanze collegate
    :parameters (?h - hero ?from - location ?to - location) ; Parametri: eroe, stanza di partenza e stanza di destinazione
    :precondition (and ; Condizioni richieste per effettuare il movimento
      (hero-at ?h ?from) ; L'eroe deve trovarsi nella stanza di partenza
      (connected ?from ?to) ; Le due stanze devono essere collegate
      (not (door-locked ?from ?to)) ; La porta tra le due stanze non deve essere bloccata
    ) ; Fine delle precondizioni di movimento
    :effect (and ; Effetti provocati dallo spostamento
      (not (hero-at ?h ?from)) ; L'eroe non si trova piu nella stanza di partenza
      (hero-at ?h ?to) ; L'eroe si trova nella nuova stanza di destinazione
    ) ; Fine degli effetti di movimento
  ) ; Chiusura dell'azione move

  (:action take-item ; Azione per raccogliere un oggetto da terra nel luogo corrente
    :parameters (?h - hero ?i - item ?l - location) ; Parametri: eroe, oggetto da raccogliere e posizione corrente
    :precondition (and ; Condizioni richieste per raccogliere l'oggetto
      (hero-at ?h ?l) ; L'eroe deve trovarsi nella stessa stanza dell'oggetto
      (item-at ?i ?l) ; L'oggetto deve essere posizionato in quel luogo
    ) ; Fine delle precondizioni di raccolta
    :effect (and ; Effetti della raccolta dell'oggetto
      (not (item-at ?i ?l)) ; L'oggetto non e piu a terra nella stanza
      (holding ?h ?i) ; L'oggetto entra a far parte dell'inventario dell'eroe
    ) ; Fine degli effetti di raccolta
  ) ; Chiusura dell'azione take-item

  (:action neutralize-drone ; Azione per distruggere o disattivare il drone ostile che blocca un passaggio
    :parameters (?h - hero ?d - drone ?from - location ?to - location) ; Parametri: eroe, drone ostile, stanza corrente e stanza bloccata
    :precondition (and ; Condizioni richieste per neutralizzare il drone
      (hero-at ?h ?from) ; L'eroe deve trovarsi nella stanza sorvegliata dal drone
      (drone-at ?d ?from) ; Il drone deve essere presente in tale stanza
      (blocked-by-drone ?from ?to ?d) ; Il drone deve stare bloccando attivamente il passaggio
    ) ; Fine delle precondizioni di attacco al drone
    :effect (and ; Effetti della neutralizzazione del drone
      (not (drone-at ?d ?from)) ; Il drone non e piu operativo nella stanza
      (not (blocked-by-drone ?from ?to ?d)) ; Il blocco sul passaggio viene rimosso rendendo accessibile la meta
    ) ; Fine degli effetti di neutralizzazione
  ) ; Chiusura dell'azione neutralize-drone

  (:action unlock-door ; Azione per sbloccare la porta di sicurezza usando la tessera magnetica
    :parameters (?h - hero ?i - item ?from - location ?to - location) ; Parametri: eroe, tessera magnetica e stanze separate dalla porta
    :precondition (and ; Condizioni necessarie per sbloccare la porta
      (hero-at ?h ?from) ; L'eroe si trova davanti alla porta bloccata
      (holding ?h ?i) ; L'eroe possiede la tessera di sicurezza
      (door-locked ?from ?to) ; La porta risulta attualmente bloccata
    ) ; Fine delle precondizioni di sblocco
    :effect (and ; Effetti dello sblocco della porta
      (not (door-locked ?from ?to)) ; La porta non e piu bloccata nella direzione di andata
      (not (door-locked ?to ?from)) ; La porta non e piu bloccata nella direzione di ritorno
    ) ; Fine degli effetti di sblocco
  ) ; Chiusura dell'azione unlock-door

  (:action disable-forcefield ; Azione per disattivare la barriera olografica usando l'EMP
    :parameters (?h - hero ?i - item ?l - location) ; Parametri: eroe, dispositivo EMP e stanza di regia
    :precondition (and ; Condizioni per sovraccaricare il campo di forza
      (hero-at ?h ?l) ; L'eroe deve essere arrivato nella sala di regia
      (holding ?h ?i) ; L'eroe deve possedere il dispositivo EMP tascabile
      (barrier-active) ; Il campo di forza deve essere attualmente attivo
    ) ; Fine delle precondizioni dell'EMP
    :effect (and ; Effetti della scarica EMP
      (not (barrier-active)) ; La barriera a campo di forza olografico viene completamente disattivata
    ) ; Fine degli effetti dell'EMP
  ) ; Chiusura dell'azione disable-forcefield

  (:action web-blind-helmet ; Azione per oscurare i sensori del casco di Mysterio con le ragnatele
    :parameters (?h - hero ?v - villain ?l - location) ; Parametri: eroe, villain e stanza corrente
    :precondition (and ; Condizioni richieste per accecare il casco
      (hero-at ?h ?l) ; L'eroe deve trovarsi nella stanza con Mysterio
      (villain-at ?v ?l) ; Mysterio deve trovarsi nella stessa stanza
      (not (barrier-active)) ; La barriera olografica protettiva deve essere stata abbattuta
      (not (helmet-blinded ?v)) ; Il casco non deve essere gia stato coperto di ragnatele
    ) ; Fine delle precondizioni per l'uso della ragnatela
    :effect (and ; Effetti dell'accecamento del casco
      (helmet-blinded ?v) ; I sensori visivi del casco di Mysterio vengono accecati
    ) ; Fine degli effetti dell'uso della ragnatela
  ) ; Chiusura dell'azione web-blind-helmet

  (:action defeat-mysterio ; Azione finale per sconfiggere fisicamente Mysterio
    :parameters (?h - hero ?v - villain ?l - location) ; Parametri: eroe, villain e stanza dello scontro
    :precondition (and ; Condizioni per poter sferrare il colpo decisivo
      (hero-at ?h ?l) ; L'eroe si trova nella stanza di regia
      (villain-at ?v ?l) ; Mysterio e presente nella stanza
      (not (barrier-active)) ; La barriera protettiva non deve essere attiva
      (helmet-blinded ?v) ; Il casco di Mysterio deve essere stato accecato per renderlo vulnerabile
      (not (defeated ?v)) ; Mysterio non deve essere gia nello stato sconfitto
    ) ; Fine delle precondizioni di sconfitta
    :effect (and ; Effetti della sconfitta del supercriminale
      (defeated ?v) ; Mysterio viene neutralizzato e sconfitto definitivamente
    ) ; Fine degli effetti di sconfitta
  ) ; Chiusura dell'azione defeat-mysterio

  (:action deactivate-gas-generator ; Azione per disattivare il macchinario che diffonde il gas allucinogeno
    :parameters (?h - hero ?dev - device ?l - location) ; Parametri: eroe, generatore di gas e luogo in cui risiede
    :precondition (and ; Condizioni necessarie per spegnere il generatore
      (hero-at ?h ?l) ; L'eroe deve trovarsi nella stanza del generatore
      (device-at ?dev ?l) ; Il dispositivo generatore deve trovarsi in questa stanza
      (not (gas-deactivated ?dev)) ; Il generatore non deve essere gia disattivato
    ) ; Fine delle precondizioni per spegnere il gas
    :effect (and ; Effetti della disattivazione del generatore
      (gas-deactivated ?dev) ; Il generatore di gas viene spento salvando la citta
    ) ; Fine degli effetti di disattivazione
  ) ; Chiusura dell'azione deactivate-gas-generator
) ; Fine della definizione del dominio PDDL


(define (problem spiderman-mysterio-studio-problem) ; Definizione del problema per la missione di Spider-Man contro Mysterio
  (:domain spiderman-mysterio-studio) ; Associazione del problema al dominio dello studio cinematografico

  (:objects ; Dichiarazione di tutte le entita presenti nello scenario
    spiderman - hero ; Spider-Man, l'eroe controllato dal giocatore
    mysterio - villain ; Quentin Beck, alias Mysterio, il supercriminale antagonista
    ingresso-studios capannone-scenografie laboratorio-effetti-speciali galleria-riflettori sala-regia - location ; Le stanze esplorabili del complesso cinematografico
    spararagnatele tessera-magnetica emp-device - item ; Gli oggetti e gadget utilizzabili durante l'avventura
    drone-proiettore - drone ; Il drone di sorveglianza olografico di Mysterio
    generatore-gas - device ; Il generatore che diffonde il letale gas allucinogeno
  ) ; Chiusura della sezione degli oggetti

  (:init ; Configurazione dello stato iniziale dell'avventura
    (hero-at spiderman ingresso-studios) ; Spider-Man inizia la missione nell'ingresso degli studi cinematografici
    (holding spiderman spararagnatele) ; Spider-Man entra nell'edificio equipaggiato con i suoi fidati spararagnatele
    (villain-at mysterio sala-regia) ; Mysterio presidia la sala di regia principale da cui controlla la struttura
    (device-at generatore-gas sala-regia) ; Il generatore di gas allucinogeno si trova pronto all'uso nella sala di regia
    (drone-at drone-proiettore capannone-scenografie) ; Il drone proiettore pattuglia l'area del capannone delle scenografie
    (item-at tessera-magnetica galleria-riflettori) ; La tessera d'accesso magnetica e posata nella galleria dei riflettori
    (item-at emp-device laboratorio-effetti-speciali) ; Il dispositivo EMP tascabile e custodito nel laboratorio effetti speciali
    (barrier-active) ; Il campo di forza olografico attorno a Mysterio e inizialmente attivo
    (connected ingresso-studios galleria-riflettori) ; Passaggio diretto dall'ingresso alla galleria dei riflettori
    (connected galleria-riflettori ingresso-studios) ; Passaggio di ritorno dalla galleria all'ingresso principale
    (connected ingresso-studios capannone-scenografie) ; Corridoio che conduce dall'ingresso al capannone delle scenografie
    (connected capannone-scenografie ingresso-studios) ; Percorso a ritroso dal capannone verso l'ingresso
    (connected capannone-scenografie laboratorio-effetti-speciali) ; Accesso dal capannone verso il laboratorio effetti speciali
    (connected laboratorio-effetti-speciali capannone-scenografie) ; Uscita dal laboratorio effetti speciali verso il capannone
    (connected ingresso-studios sala-regia) ; Porta blindata principale che separa l'ingresso dalla sala di regia
    (connected sala-regia ingresso-studios) ; Porta di sicurezza vista dall'interno della sala di regia
    (blocked-by-drone capannone-scenografie laboratorio-effetti-speciali drone-proiettore) ; Il drone proiettore sbarra il varco per il laboratorio
    (door-locked ingresso-studios sala-regia) ; La porta della sala di regia e bloccata dal sistema elettronico
    (door-locked sala-regia ingresso-studios) ; Il blocco della porta di sicurezza e attivo in entrambe le direzioni
  ) ; Chiusura della definizione dello stato iniziale

  (:goal ; Condizioni necessarie per completare con successo la missione
    (and ; Tutte le condizioni devono essere verificate contemporaneamente
      (hero-at spiderman sala-regia) ; Spider-Man deve aver raggiunto la sala di regia
      (gas-deactivated generatore-gas) ; Il generatore di gas allucinogeno deve essere stato spento
      (defeated mysterio) ; Mysterio deve essere stato definitivamente sconfitto
    ) ; Fine della congiunzione degli obiettivi
  ) ; Chiusura della sezione degli obiettivi
) ; Fine del file problema PDDL