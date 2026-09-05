(define (domain blocks-world)
  (:requirements :strips :typing)
  (:types block)

  (:predicates
    (on ?x - block ?y - block)   ; ?x è sopra ?y
    (on-table ?x - block)        ; ?x è sul tavolo
    (clear ?x - block)           ; nessun blocco è sopra ?x
    (handempty)                  ; la mano è libera
    (holding ?x - block)         ; la mano tiene ?x
  )

  (:action pick-up
    :parameters (?b - block)
    :precondition (and (on-table ?b) (clear ?b) (handempty))
    :effect (and (not (on-table ?b))
                 (not (clear ?b))
                 (not (handempty))
                 (holding ?b))
  )

  (:action put-down
    :parameters (?b - block)
    :precondition (holding ?b)
    :effect (and (not (holding ?b))
                 (handempty)
                 (on-table ?b)
                 (clear ?b))
  )

  (:action stack
    :parameters (?b - block ?c - block)
    :precondition (and (holding ?b) (clear ?c))
    :effect (and (not (holding ?b))
                 (not (clear ?c))
                 (handempty)
                 (on ?b ?c)
                 (clear ?b))
  )

  (:action unstack
    :parameters (?b - block ?c - block)
    :precondition (and (on ?b ?c) (clear ?b) (handempty))
    :effect (and (not (on ?b ?c))
                 (not (handempty))
                 (not (clear ?c))
                 (clear ?c)
                 (holding ?b))
  )
)
(define (problem blocks-example-3)
  (:domain blocks-world)

  (:objects
    a - block
    b - block
    c - block
  )

  (:init
    (on-table a)
    (on b a)
    (on c b)
    (clear c)
    (handempty)
  )

  (:goal
    (and (on a b)
         (on b c)
         (on-table c))
  )
)
