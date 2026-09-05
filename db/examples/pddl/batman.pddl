(define (domain batman-rescue) ; definizione del dominio
  (:requirements :typing) ; richiede il typing
  (:types
    person location bomb) ; tipi di oggetti: persone, luoghi, bombe
  (:predicates
    (at ?p - person ?l - location) ; ?p si trova in ?l
    (trapped ?p - person) ; ?p è intrappolato
    (bomb-at ?b - bomb ?l - location) ; la bomba ?b è posizionata in ?l
    (defused ?b - bomb) ; la bomba ?b è stata disinnescata
    (escaped ?p - person) ; ?p è uscito dal campanile
  ) ; fine dichiarazione predicati
  (:action move
    :parameters (?p - person ?from - location ?to - location) ; parametri: chi si muove da dove a dove
    :precondition (and (at ?p ?from)) ; precondizione: ?p è attualmente in ?from
    :effect (and (not (at ?p ?from)) (at ?p ?to)) ; effetto: ?p non è più in ?from ma è in ?to
  ) ; fine azione move
  (:action rescue
    :parameters (?bat - person ?worker - person ?l - location) ; parametri: Batman, operaio, luogo comune
    :precondition (and (at ?bat ?l) (at ?worker ?l) (trapped ?worker)) ; precondizioni: entrambi nello stesso luogo e operaio intrappolato
    :effect (and (not (trapped ?worker)) (escaped ?worker)) ; effetto: operaio non più intrappolato e considerato uscito
  ) ; fine azione rescue
  (:action defuse-bomb
    :parameters (?bat - person ?b - bomb ?l - location) ; parametri: Batman, bomba, luogo della bomba
    :precondition (and (at ?bat ?l) (bomb-at ?b ?l) (not (defused ?b))) ; precondizioni: Batman è nello stesso luogo della bomba non ancora disinnescata
    :effect (and (defused ?b)) ; effetto: la bomba viene disinnescata
  ) ; fine azione defuse-bomb
  (:action exit
    :parameters (?p - person ?l - location) ; parametri: chi esce e da quale luogo
    :precondition (and (at ?p ?l) (not (trapped ?p))) ; precondizione: ?p è in ?l e non è intrappolato
    :effect (and (escaped ?p) (not (at ?p ?l))) ; effetto: ?p è fuori dal campanile e non più in ?l
  ) ; fine azione exit
) ; fine definizione dominio


(define (problem batman-rescue-problem) ; definizione del problema
  (:domain batman-rescue) ; riferimento al dominio fornito
  (:objects
    batman worker joker - person ; i personaggi: Batman, l'operaio e Joker
    ground stair hallway campanile - location ; i luoghi della missione
    bomb1 - bomb ; la bomba posizionata nel campanile
  ) ; fine dichiarazione oggetti
  (:init
    (at batman ground) ; Batman parte dal suolo
    (at worker campanile) ; L'operaio è nel campanile
    (trapped worker) ; L'operaio è intrappolato
    (at joker hallway) ; Joker si trova nel corridoio
    (bomb-at bomb1 campanile) ; La bomba è nel campanile
  ) ; fine stato iniziale
  (:goal
    (and
      (escaped worker) ; l'operaio deve essere salvato e considerato uscito
      (escaped batman) ; Batman deve uscire dal campanile
      (defused bomb1) ; la bomba deve essere disinnescata (obiettivo opzionale)
    )
  ) ; fine definizione goal
) ; fine del problema