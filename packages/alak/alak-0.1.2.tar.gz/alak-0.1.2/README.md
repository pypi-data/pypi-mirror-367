#  Alak

**Alak** is a fun, Tagalog-inspired esolang designed for learning and laughs. It uses Filipino "inuman" terms as syntax.

---

## Getting Started

To install type:

```
pip install alak
```

### Usage
```bash
alak init # Creates hello.alak
alak repl # Launches interactive REPL shell
alak run hello.alak # Runs the program
alak --version # Outputs: alak version 0.1.0
```

### Supported Features in AlakLang

🔹 Variable Declaration
Use alak to declare and initialize a variable:
```
alak x = 5;
alak y = 10;
```

You can also use Boolean values:

```
alak sanMigApple = walangTama; // false
alak alfonsoBrandy = myTama;   // true
```

* Use tungga to print expressions or strings (with variable interpolation):
```
tungga x;
tungga "Total ay {x}";
```

🔹 Comments
Alak supports c-style comment:

```
// Ito ay comment pare!
```

🔹 If Statement
Use ```kung```, ```tagay```, and ```bitaw``` for conditional logic:

```
kung (x < y) tagay
    tungga "{x} pesos ay kaunti sa ambag na {y}";
bitaw
```

🔹 While Loop
Use ```ikot```, ```tagay```, and ```bitaw``` for looping:

```
ikot (x < 10) tagay
    tungga x;
    alak x = x + 1;
bitaw
```

🔹 Function Definition & Calling
Use ```inom``` to define a function and call it like normal:

```
inom ginebra(a, b) tagay
    alak sum = a + b;
    tungga "Total ng tinagay ng tropa ay {sum}";
bitaw

ginebra(3, 5);
```

🔹 Arrays & Indexing
Declare arrays using square brackets ```[]``` and access elements using indices:

```
alak tropa = ["Mark", "Leetz", "Leo"];
tungga tropa[0];
tungga tropa[1];
```

* Tagay-style For Loop: ```hangOver```

```
hangOver alak i = 0; i < 3; i = i + 1 tagay
    tungga "Shot #{i}";
bitaw
```

* Input from User with ```ambag()```

```
alak pare = ambag("Sino nag ambag? ");
tungga "Salamat {pare}!";
```

* Built in functions

```
alak word = "alak";
alak length = haba(word);
tungga "Haba ng '{word}' ay {length}";

alak name = "leetz";
alak shout = taasTagay(name);
tungga "Tagay kay {shout}!";

alak tropa = ["leetz", "mark"];
alak x = "joseph";

tropa.nahilo(x);      // append "joseph" to array
tungga "{tropa[2]} ay bagong tropa!";   // joseph ay bagong tropa!


// lagok
alak shot = lagok(1, 5);
alak inumin = ["GSM", "Empe", "SanMig"];
alak randomInom = lagok(inumin);
tungga "Tinagay ay {randomInom}, dami: {shot}"; // Tinagay ay ['GSM', 'Empe', 'SanMig'], dami: 1.0
```

* Exit Program with ```patayNa()```

```
tungga "Lasing na, uwian na!";
patayNa();
```

### REPL Example
You can test single lines of Alak code interactively using the REPL:

```bash
alak repl
```

output:
```bash
alak> alak a = 3;
alak> alak b = 5;
alak> tungga a + b;
8.0
alak> exit
```


## New Keywords (Under development)
* May hangover pa ako, pero gagawin ko pa ito pare!!!

1. ```balikTagay``` Return Statements

```bash
inom add(a, b) tagay
    balikTagay a + b;
bitaw

alak nahilo = add(3, 5);
tungga nahilo;

```

2. Error Handling with ```sukaException```

```
try tagay
    alak x = 5 / 0;
bitaw sukaException
    tungga "Sumuka si tropa. Walang division by sero, pare!";
bitaw
```

3. Call Functions with ```kalabit```

```
inom paShot() tagay
    tungga "Kampay!";
bitaw

kalabit paShot;
```

### License
MIT License. Feel free to use and modify.
