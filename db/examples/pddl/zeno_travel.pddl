(define (domain zeno-travel)
  (:requirements :typing)
  (:types
    aircraft person city flevel - object
  )

  (:predicates
    (at ?x - (either person aircraft) ?c - city)
    (in ?p - person ?a - aircraft)
    (fuel-level ?a - aircraft ?l - flevel)
    (next ?l1 ?l2 - flevel)
  )

  (:action board
    :parameters (?p - person ?a - aircraft ?c - city)
    :precondition (and (at ?p ?c) (at ?a ?c))
    :effect      (and (not (at ?p ?c))
                      (in ?p ?a))
  )

  (:action debark
    :parameters (?p - person ?a - aircraft ?c - city)
    :precondition (and (in ?p ?a) (at ?a ?c))
    :effect      (and (not (in ?p ?a))
                      (at ?p ?c))
  )

  (:action fly
    :parameters (?a - aircraft ?c1 ?c2 - city ?l1 ?l2 - flevel)
    :precondition (and (at ?a ?c1)
                       (fuel-level ?a ?l1)
                       (next ?l2 ?l1))
    :effect (and (not (at ?a ?c1))
                 (at ?a ?c2)
                 (not (fuel-level ?a ?l1))
                 (fuel-level ?a ?l2))
  )

  (:action refuel
    :parameters (?a - aircraft ?c - city ?l1 ?l2 - flevel)
    :precondition (and (at ?a ?c)
                       (fuel-level ?a ?l1)
                       (next ?l1 ?l2))
    :effect (and (fuel-level ?a ?l2)
                 (not (fuel-level ?a ?l1)))
  )
)

(define (problem ZTRAVEL-1-2)
  (:domain zeno-travel)

  (:objects
    plane1 - aircraft
    person1 - person
    person2 - person
    city0 - city
    city1 - city
    city2 - city
    fl0 fl1 fl2 fl3 fl4 fl5 fl6 - flevel
  )

  (:init
    (at plane1 city0)
    (fuel-level plane1 fl1)
    (at person1 city0)
    (at person2 city2)
    (next fl0 fl1)
    (next fl1 fl2)
    (next fl2 fl3)
    (next fl3 fl4)
    (next fl4 fl5)
    (next fl5 fl6)
  )

  (:goal
    (and (at plane1 city1)
         (at person1 city0)
         (at person2 city2))
  )
)

