% 1. Существует к указанному году
exists_at(P, Y) :- birth(P, B), Y >= B.

% 2. Жив к году Y
alive_at(P, Y) :-
    birth(P, B), Y >= B,
    \+ (death(P, D), D =< Y).

% 3. Умер к году Y
dead_at(P, Y) :- death(P, D), D =< Y.

% 4. Возраст в году Y
age_at(P, Y, Age) :- alive_at(P, Y), birth(P, B), Age is Y - B.

% 5–6. Старше/младше в году Y
older_than_at(A, B, Y) :- age_at(A, Y, A1), age_at(B, Y, B1), A1 > B1.
younger_than_at(A, B, Y) :- older_than_at(B, A, Y).

% 7–8. Брак
wedded(P1, P2, Y) :- marriage(P1, P2, Y).
wedded(P1, P2, Y) :- marriage(P2, P1, Y).

% 9. Состоят в браке к году Y
married_at(P1, P2, Y) :-
    wedded(P1, P2, M), M =< Y,
    \+ (divorce(P1, P2, D), D =< Y).

% 10. Супруг в году Y
spouse_at(P, Sp, Y) :- married_at(P, Sp, Y).

% 11. Холост/не замужем в году Y
single_at(P, Y) :- exists_at(P, Y), \+ spouse_at(P, _, Y).

% 12. Вдова/вдовец в году Y
widowed_at(P, Sp, Y) :-
    wedded(P, Sp, M), M =< Y,
    death(Sp, Ds), Ds =< Y,
    alive_at(P, Y),
    \+ married_at(P, Sp, Y).

% 13–14. Интервал брака и его длительность
marriage_interval(P1, P2, Start, End) :-
    wedded(P1, P2, Start),
    ( divorce(P1, P2, End)
    ; death(P1, End)
    ; death(P2, End)
    ; End = inf ).

marriage_duration(P1, P2, D) :-
    marriage_interval(P1, P2, S, E),
    E \= inf, D is E - S.

% 15. Год первого брака
first_marriage_year(P, Ymin) :-
    setof(Y, Sp^wedded(P, Sp, Y), [Ymin|_]).


% 16–17. Мать / отец
mother(M, C) :- female(M), parent(M, C).
father(F, C) :- male(F), parent(F, C).

% 18. Ребёнок
child(C, P) :- parent(P, C).

% 19. Другой родитель ребёнка
co_parent(P, Other, C) :- parent(P, C), parent(Other, C), P \= Other.

% 20–21. Бабушка/дедушка и внуки
grandparent(G, C) :- parent(G, P), parent(P, C).
grandchild(C, G) :- grandparent(G, C).

% 22–23. Предки/потомки (рекурсивно)
ancestor(A, D) :- parent(A, D).
ancestor(A, D) :- parent(A, X), ancestor(X, D).
descendant(D, A) :- ancestor(A, D).

% 24–25. Подсчёт детей и потомков
children_count(P, N) :- findall(C, parent(P, C), L), length(L, N).
descendants_count(P, N) :- findall(D, descendant(D, P), L), sort(L, U), length(U, N).

% 26–27. Сиблинги: полные и неполные
sibling(A, B) :- parent(P, A), parent(P, B), A \= B.
full_sibling(A, B) :- mother(M, A), mother(M, B), father(F, A), father(F, B), A \= B.
half_sibling(A, B) :- sibling(A, B), \+ full_sibling(A, B).

% 28–29. Дяди/тёти и кузены
uncle_aunt(U, S) :- parent(P, S), sibling(U, P).
cousin(A, B) :- parent(P1, A), parent(P2, B), sibling(P1, P2), A \= B.

