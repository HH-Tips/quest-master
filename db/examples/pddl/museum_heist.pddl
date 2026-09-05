(define (domain museum-heist) ; definisce il dominio per il furto al museo
  (:requirements :typing :strips) ; richiede tipizzazione e operazioni STRIPS
  (:types
    person guard location artifact case tool) ; tipi di oggetti presenti nel dominio
  (:predicates
    (at ?x - (either person guard) ?l - location) ; ?x si trova nella location ?l
    (connected ?l1 - location ?l2 - location) ; le location ?l1 e ?l2 sono adiacenti
    (has-tool ?p - person ?t - tool) ; la persona ?p possiede lo strumento ?t
    (case-locked ?c - case) ; la teca ?c è chiusa a chiave
    (alarm-active ?c - case) ; il sistema di allarme della teca ?c è attivo
    (at-case ?c - case ?l - location) ; la teca ?c si trova nella location ?l
    (artifact-in-case ?a - artifact ?c - case) ; l'artefatto ?a è contenuto nella teca ?c
    (carrying ?p - person ?a - artifact) ; la persona ?p sta trasportando l'artefatto ?a
    (guard-neutralized ?g - guard) ; la guardia ?g è stata neutralizzata
  ) ; fine della sezione predicati

  (:action move
    :parameters (?p - person ?from - location ?to - location) ; muove il ladro da ?from a ?to
    :precondition (and (at ?p ?from) (connected ?from ?to)) ; il ladro è in ?from e le due location sono collegate
    :effect (and (not (at ?p ?from)) (at ?p ?to)) ; il ladro non è più in ?from e ora è in ?to
  ) ; fine azione move

  (:action tranquilize-guard
    :parameters (?p - person ?g - guard ?l - location) ; usa la pistola per neutralizzare una guardia in ?l
    :precondition (and (at ?p ?l) (at ?g ?l) (has-tool ?p pistol)) ; ladro e guardia nella stessa location e ladro possiede la pistola
    :effect (and (guard-neutralized ?g) (not (at ?g ?l))) ; la guardia è neutralizzata e non è più considerata presente
  ) ; fine azione tranquilize-guard

  (:action unlock-case
    :parameters (?p - person ?c - case ?l - location) ; apre la teca usando uno strumento appropriato
    :precondition (and (at ?p ?l) (at-case ?c ?l) (has-tool ?p toolbox) (case-locked ?c)) ; ladro è nella stessa location della teca, possiede la cassetta degli attrezzi e la teca è chiusa
    :effect (and (not (case-locked ?c))) ; la teca non è più chiusa
  ) ; fine azione unlock-case

  (:action disable-alarm
    :parameters (?p - person ?c - case ?l - location) ; disattiva l'allarme della teca
    :precondition (and (at ?p ?l) (at-case ?c ?l) (has-tool ?p toolbox) (alarm-active ?c)) ; ladro è nella stessa location, possiede la cassetta degli attrezzi e l'allarme è attivo
    :effect (and (not (alarm-active ?c))) ; l'allarme è ora disattivato
  ) ; fine azione disable-alarm

  (:action take-artifact
    :parameters (?p - person ?a - artifact ?c - case ?l - location) ; prende l'artefatto dalla teca
    :precondition (and (at ?p ?l) (at-case ?c ?l) (artifact-in-case ?a ?c) (not (case-locked ?c)) (not (alarm-active ?c))) ; ladro è nella stessa location, l'artefatto è nella teca, la teca è sbloccata e l'allarme è spento
    :effect (and (not (artifact-in-case ?a ?c)) (carrying ?p ?a)) ; l'artefatto non è più nella teca e il ladro lo porta con sé
  ) ; fine azione take-artifact

  (:action exit-museum
    :parameters (?p - person ?from - location ?exit - location) ; esce dal museo verso l'uscita
    :precondition (and (at ?p ?from) (connected ?from ?exit) (not (guard-neutralized ?g))) ; il ladro è nella location interna, l'uscita è collegata e non c'è guardia non neutralizzata nella stessa location
    :effect (and (not (at ?p ?from)) (at ?p ?exit)) ; il ladro non è più dentro e ora è fuori
  ) ; fine azione exit-museum
) ; fine definizione del dominio


(define (problem museum-heist-quest) ; definizione del problema
  (:domain museum-heist) ; dominio associato
  (:objects
    thief - person ; il ladro protagonista
    guard1 guard2 - guard ; le due guardie di turno
    entrance hallway gallery security exit - location ; le location del museo
    case1 - case ; la teca di sicurezza contenente l'artefatto
    gem - artifact ; l'artefatto da rubare
    pistol toolbox torch gloves - tool ; gli strumenti a disposizione del ladro
  ) ; fine dichiarazione oggetti
  (:init
    (at thief entrance) ; il ladro parte dall'ingresso
    (at guard1 entrance) ; guardia 1 è all'ingresso
    (at guard2 hallway) ; guardia 2 è nel corridoio
    (connected entrance hallway) ; ingresso collegato al corridoio
    (connected hallway entrance) ; corridoio collegato all'ingresso
    (connected hallway gallery) ; corridoio collegato alla galleria principale
    (connected gallery hallway) ; galleria collegata al corridoio
    (connected gallery security) ; galleria collegata alla stanza di sicurezza
    (connected security gallery) ; stanza di sicurezza collegata alla galleria
    (connected security exit) ; stanza di sicurezza collegata all'uscita
    (connected exit security) ; uscita collegata alla stanza di sicurezza
    (connected gallery exit) ; galleria collegata direttamente all'uscita (ramificazione)
    (connected exit gallery) ; uscita collegata alla galleria
    (has-tool thief pistol) ; il ladro possiede la pistola tranquillizzante
    (has-tool thief toolbox) ; il ladro possiede la cassetta degli attrezzi
    (has-tool thief torch) ; il ladro possiede la torcia
    (has-tool thief gloves) ; il ladro possiede i guanti
    (case-locked case1) ; la teca è chiusa a chiave
    (alarm-active case1) ; l'allarme della teca è attivo
    (at-case case1 gallery) ; la teca si trova nella galleria principale
    (artifact-in-case gem case1) ; la gemma è all'interno della teca
  ) ; fine stato iniziale
  (:goal
    (and
      (carrying thief gem) ; il ladro ha in mano la gemma
      (at thief exit) ; il ladro si trova fuori dal museo
    ) ; fine congiunzione goal
  ) ; fine sezione goal
) ; fine definizione del problema
