from symcalc.plugins.additions.aliases import AddAliases
from tests import TestCalculator


def test_plugin_aliases_instantiate():
    AddAliases()


def test_plugin_aliases_hook():
    calc = TestCalculator()
    plugin = AddAliases()
    calc.register_plugin(plugin)
    assert plugin in calc.plugins


def test_plugin_aliases_context_updated():
    calc = TestCalculator()
    calc.register_plugin(AddAliases())
    assert calc.chksym("mksym")
    assert calc.chksym("plot_3d")
    assert calc.chksym("plot_3d_parametric_line")
    assert calc.chksym("plot_3d_parametric_surface")
    assert calc.chksym("graph")
    assert calc.chksym("graph_implicit")
    assert calc.chksym("graph_parametric")
    assert calc.chksym("graph3d")
    assert calc.chksym("graph3d_parametric_line")
    assert calc.chksym("graph3d_parametric_surface")
    assert calc.chksym("differentiate")
    assert calc.chksym("arcsin")
    assert calc.chksym("arccos")
    assert calc.chksym("arctan")
    assert calc.chksym("arcsec")
    assert calc.chksym("arccsc")
    assert calc.chksym("arccot")
    assert calc.chksym("arcsinh")
    assert calc.chksym("arccosh")
    assert calc.chksym("arctanh")
    assert calc.chksym("arcsech")
    assert calc.chksym("arccsch")
    assert calc.chksym("arccoth")
    assert calc.chksym("sindeg")
    assert calc.chksym("cosdeg")
    assert calc.chksym("tandeg")
    assert calc.chksym("secdeg")
    assert calc.chksym("cscdeg")
    assert calc.chksym("cotdeg")
    assert calc.chksym("asindeg")
    assert calc.chksym("acosdeg")
    assert calc.chksym("atandeg")
    assert calc.chksym("asecdeg")
    assert calc.chksym("acscdeg")
    assert calc.chksym("acotdeg")
    assert calc.chksym("arcsindeg")
    assert calc.chksym("arccosdeg")
    assert calc.chksym("arctandeg")
    assert calc.chksym("arcsecdeg")
    assert calc.chksym("arccscdeg")
    assert calc.chksym("arccotdeg")

    assert callable(calc.getsym("mksym"))
    assert callable(calc.getsym("plot_3d"))
    assert callable(calc.getsym("plot_3d_parametric_line"))
    assert callable(calc.getsym("plot_3d_parametric_surface"))
    assert callable(calc.getsym("graph"))
    assert callable(calc.getsym("graph_implicit"))
    assert callable(calc.getsym("graph_parametric"))
    assert callable(calc.getsym("graph3d"))
    assert callable(calc.getsym("graph3d_parametric_line"))
    assert callable(calc.getsym("graph3d_parametric_surface"))
    assert callable(calc.getsym("differentiate"))
    assert callable(calc.getsym("arcsin"))
    assert callable(calc.getsym("arccos"))
    assert callable(calc.getsym("arctan"))
    assert callable(calc.getsym("arcsec"))
    assert callable(calc.getsym("arccsc"))
    assert callable(calc.getsym("arccot"))
    assert callable(calc.getsym("arcsinh"))
    assert callable(calc.getsym("arccosh"))
    assert callable(calc.getsym("arctanh"))
    assert callable(calc.getsym("arcsech"))
    assert callable(calc.getsym("arccsch"))
    assert callable(calc.getsym("arccoth"))
    assert callable(calc.getsym("sindeg"))
    assert callable(calc.getsym("cosdeg"))
    assert callable(calc.getsym("tandeg"))
    assert callable(calc.getsym("secdeg"))
    assert callable(calc.getsym("cscdeg"))
    assert callable(calc.getsym("cotdeg"))
    assert callable(calc.getsym("asindeg"))
    assert callable(calc.getsym("acosdeg"))
    assert callable(calc.getsym("atandeg"))
    assert callable(calc.getsym("asecdeg"))
    assert callable(calc.getsym("acscdeg"))
    assert callable(calc.getsym("acotdeg"))
    assert callable(calc.getsym("arcsindeg"))
    assert callable(calc.getsym("arccosdeg"))
    assert callable(calc.getsym("arctandeg"))
    assert callable(calc.getsym("arcsecdeg"))
    assert callable(calc.getsym("arccscdeg"))
    assert callable(calc.getsym("arccotdeg"))


def test_plugin_aliases_available():
    calc = TestCalculator()
    calc.register_plugin(AddAliases())
    assert callable(calc.command("mksym"))
    assert callable(calc.command("plot_3d"))
    assert callable(calc.command("plot_3d_parametric_line"))
    assert callable(calc.command("plot_3d_parametric_surface"))
    assert callable(calc.command("graph"))
    assert callable(calc.command("graph_implicit"))
    assert callable(calc.command("graph_parametric"))
    assert callable(calc.command("graph3d"))
    assert callable(calc.command("graph3d_parametric_line"))
    assert callable(calc.command("graph3d_parametric_surface"))
    assert callable(calc.command("differentiate"))
    assert callable(calc.command("arcsin"))
    assert callable(calc.command("arccos"))
    assert callable(calc.command("arctan"))
    assert callable(calc.command("arcsec"))
    assert callable(calc.command("arccsc"))
    assert callable(calc.command("arccot"))
    assert callable(calc.command("arcsinh"))
    assert callable(calc.command("arccosh"))
    assert callable(calc.command("arctanh"))
    assert callable(calc.command("arcsech"))
    assert callable(calc.command("arccsch"))
    assert callable(calc.command("arccoth"))
    assert callable(calc.command("sindeg"))
    assert callable(calc.command("cosdeg"))
    assert callable(calc.command("tandeg"))
    assert callable(calc.command("secdeg"))
    assert callable(calc.command("cscdeg"))
    assert callable(calc.command("cotdeg"))
    assert callable(calc.command("asindeg"))
    assert callable(calc.command("acosdeg"))
    assert callable(calc.command("atandeg"))
    assert callable(calc.command("asecdeg"))
    assert callable(calc.command("acscdeg"))
    assert callable(calc.command("acotdeg"))
    assert callable(calc.command("arcsindeg"))
    assert callable(calc.command("arccosdeg"))
    assert callable(calc.command("arctandeg"))
    assert callable(calc.command("arcsecdeg"))
    assert callable(calc.command("arccscdeg"))
    assert callable(calc.command("arccotdeg"))


def test_plugin_aliases_degree_conversion():
    calc = TestCalculator()
    calc.register_plugin(AddAliases())

    assert calc.command("sindeg(0)") == 0
    assert calc.command("cosdeg(0)") == 1
    assert calc.command("tandeg(0)") == 0
    # assert calc.command("cscdeg(0)") == 0
    assert calc.command("secdeg(0)") == 1
    # assert calc.command("tandeg(0)") == 0

    assert calc.command("sindeg(30)") == calc.command("S(1)/2")
    assert calc.command("cosdeg(30)") == calc.command("sqrt(S(3))/2")
    assert calc.command("tandeg(30)") == calc.command("sqrt(S(3))/3")
    assert calc.command("cscdeg(30)") == 2
    assert calc.command("secdeg(30)") == calc.command("2/sqrt(S(3))")
    assert calc.command("cotdeg(30)") == calc.command("3/sqrt(S(3))")
    assert calc.command("sindeg(45)") == calc.command("sqrt(S(2))/2")
    assert calc.command("cosdeg(45)") == calc.command("sqrt(S(2))/2")
    assert calc.command("tandeg(45)") == 1
    assert calc.command("cscdeg(45)") == calc.command("2/sqrt(S(2))")
    assert calc.command("secdeg(45)") == calc.command("2/sqrt(S(2))")
    assert calc.command("cotdeg(45)") == 1
    assert calc.command("sindeg(60)") == calc.command("sqrt(S(3))/2")
    assert calc.command("cosdeg(60)") == calc.command("S(1)/2")
    assert calc.command("tandeg(60)") == calc.command("sqrt(S(3))")
    assert calc.command("cscdeg(60)") == calc.command("2/sqrt(S(3))")
    assert calc.command("secdeg(60)") == 2
    assert calc.command("cotdeg(60)") == calc.command("1/sqrt(S(3))")
    assert calc.command("sindeg(90)") == 1
    assert calc.command("cosdeg(90)") == 0
    # assert calc.command("tandeg(90)") == 0
    # assert calc.command("secdeg(90)") == 0
    assert calc.command("cscdeg(90)") == 1
    # assert calc.command("cotdeg(90)") == 0
    assert calc.command("sindeg(120)") == calc.command("sqrt(S(3))/2")
    assert calc.command("cosdeg(120)") == calc.command("-S(1)/2")
    assert calc.command("tandeg(120)") == calc.command("-sqrt(S(3))")
    assert calc.command("cscdeg(120)") == calc.command("2/sqrt(S(3))")
    assert calc.command("secdeg(120)") == -2
    assert calc.command("cotdeg(120)") == calc.command("-1/sqrt(S(3))")
    assert calc.command("sindeg(150)") == calc.command("S(1)/2")
    assert calc.command("cosdeg(150)") == calc.command("-sqrt(S(3))/2")
    assert calc.command("tandeg(150)") == calc.command("-sqrt(S(3))/3")
    assert calc.command("cscdeg(150)") == 2
    assert calc.command("secdeg(150)") == calc.command("-2/sqrt(S(3))")
    assert calc.command("cotdeg(150)") == calc.command("-3/sqrt(S(3))")
    assert calc.command("sindeg(180)") == 0
    assert calc.command("cosdeg(180)") == -1
    assert calc.command("tandeg(180)") == 0
    # assert calc.command("cscdeg(180)") == 0
    assert calc.command("secdeg(180)") == -1
    # assert calc.command("tandeg(180)") == 0

    assert calc.command("sindeg(-30)") == calc.command("-S(1)/2")
    assert calc.command("cosdeg(-30)") == calc.command("sqrt(S(3))/2")
    assert calc.command("tandeg(-30)") == calc.command("-sqrt(S(3))/3")
    assert calc.command("cscdeg(-30)") == -2
    assert calc.command("secdeg(-30)") == calc.command("2/sqrt(S(3))")
    assert calc.command("cotdeg(-30)") == calc.command("-3/sqrt(S(3))")
    assert calc.command("sindeg(-45)") == calc.command("-sqrt(S(2))/2")
    assert calc.command("cosdeg(-45)") == calc.command("sqrt(S(2))/2")
    assert calc.command("tandeg(-45)") == -1
    assert calc.command("cscdeg(-45)") == calc.command("-2/sqrt(S(2))")
    assert calc.command("secdeg(-45)") == calc.command("2/sqrt(S(2))")
    assert calc.command("cotdeg(-45)") == -1
    assert calc.command("sindeg(-60)") == calc.command("-sqrt(S(3))/2")
    assert calc.command("cosdeg(-60)") == calc.command("S(1)/2")
    assert calc.command("tandeg(-60)") == calc.command("-sqrt(S(3))")
    assert calc.command("cscdeg(-60)") == calc.command("-2/sqrt(S(3))")
    assert calc.command("secdeg(-60)") == 2
    assert calc.command("cotdeg(-60)") == calc.command("-1/sqrt(S(3))")
    assert calc.command("sindeg(-90)") == -1
    assert calc.command("cosdeg(-90)") == 0
    # assert calc.command("tandeg(-90)") == 0
    # assert calc.command("secdeg(-90)") == 0
    assert calc.command("cscdeg(-90)") == -1
    # assert calc.command("cotdeg(-90)") == 0
    assert calc.command("sindeg(-120)") == calc.command("-sqrt(S(3))/2")
    assert calc.command("cosdeg(-120)") == calc.command("-S(1)/2")
    assert calc.command("tandeg(-120)") == calc.command("sqrt(S(3))")
    assert calc.command("cscdeg(-120)") == calc.command("-2/sqrt(S(3))")
    assert calc.command("secdeg(-120)") == -2
    assert calc.command("cotdeg(-120)") == calc.command("1/sqrt(S(3))")
    assert calc.command("sindeg(-150)") == calc.command("-S(1)/2")
    assert calc.command("cosdeg(-150)") == calc.command("-sqrt(S(3))/2")
    assert calc.command("tandeg(-150)") == calc.command("sqrt(S(3))/3")
    assert calc.command("cscdeg(-150)") == -2
    assert calc.command("secdeg(-150)") == calc.command("-2/sqrt(S(3))")
    assert calc.command("cotdeg(-150)") == calc.command("3/sqrt(S(3))")
    assert calc.command("sindeg(-180)") == 0
    assert calc.command("cosdeg(-180)") == -1
    assert calc.command("tandeg(-180)") == 0
    # assert calc.command("cscdeg(-180)") == 0
    assert calc.command("secdeg(-180)") == -1
    # assert calc.command("tandeg(-180)") == 0

    for n in range(1, 10):
        for d in range(0, 360, 10):
            assert calc.command(f"sindeg({d}).evalf()") == calc.command(f"sindeg({d + 360*n}).evalf*(") == calc.command(f"sindeg({d - 360*n}).evalf()")
            assert calc.command(f"cosdeg({d}).evalf()") == calc.command(f"cosdeg({d + 360*n}).evalf*(") == calc.command(f"cosdeg({d - 360*n}).evalf()")
            assert calc.command(f"tandeg({d}).evalf()") == calc.command(f"tandeg({d + 180*n}).evalf*(") == calc.command(f"tandeg({d - 180*n}).evalf()")
            assert calc.command(f"secdeg({d}).evalf()") == calc.command(f"secdeg({d + 360*n}).evalf*(") == calc.command(f"secdeg({d - 360*n}).evalf()")
            assert calc.command(f"cscdeg({d}).evalf()") == calc.command(f"cscdeg({d + 360*n}).evalf*(") == calc.command(f"cscdeg({d - 360*n}).evalf()")
            assert calc.command(f"cotdeg({d}).evalf()") == calc.command(f"cotdeg({d + 180*n}).evalf*(") == calc.command(f"cotdeg({d - 180*n}).evalf()")


def test_plugin_aliases_invdegree_conversion():
    calc = TestCalculator()
    calc.register_plugin(AddAliases())

    assert calc.command("asindeg(0)") == 0
    assert calc.command("acosdeg(0)") == 90
    assert calc.command("atandeg(0)") == 0

    assert calc.command("asindeg(S(1)/2)") == 30
    assert calc.command("acosdeg(sqrt(S(3))/2)") == 30
    assert calc.command("atandeg(sqrt(S(3))/3)") == 30
    assert calc.command("acscdeg(2)") == 30
    assert calc.command("asecdeg(2/sqrt(S(3)))") == 30
    assert calc.command("acotdeg(3/sqrt(S(3)))") == 30
    assert calc.command("asindeg(sqrt(S(2))/2)") == 45
    assert calc.command("acosdeg(sqrt(S(2))/2)") == 45
    assert calc.command("atandeg(1)") == 45
    assert calc.command("acscdeg(2/sqrt(S(2)))") == 45
    assert calc.command("asecdeg(2/sqrt(S(2)))") == 45
    assert calc.command("acotdeg(1)") == 45
    assert calc.command("asindeg(sqrt(S(3))/2)") == 60
    assert calc.command("acosdeg(S(1)/2)") == 60
    assert calc.command("atandeg(sqrt(S(3)))") == 60
    assert calc.command("acscdeg(2/sqrt(S(3)))") == 60
    assert calc.command("asecdeg(2)") == 60
    assert calc.command("acotdeg(1/sqrt(S(3)))") == 60
    assert calc.command("asindeg(1)") == 90
    assert calc.command("acosdeg(0)") == 90
    assert calc.command("acscdeg(1)") == 90

    assert calc.command("asindeg(-S(1)/2)") == -30
    assert calc.command("atandeg(-sqrt(S(3))/3)") == -30
    assert calc.command("acscdeg(-2)") == -30
    assert calc.command("acotdeg(-3/sqrt(S(3)))") == -30
    assert calc.command("asindeg(-sqrt(S(2))/2)") == -45
    assert calc.command("atandeg(-1)") == -45
    assert calc.command("acscdeg(-2/sqrt(S(2)))") == -45
    assert calc.command("acotdeg(-1)") == -45
    assert calc.command("asindeg(-sqrt(S(3))/2)") == -60
    assert calc.command("atandeg(-sqrt(S(3)))") == -60
    assert calc.command("acscdeg(-2/sqrt(S(3)))") == -60
    assert calc.command("acotdeg(-1/sqrt(S(3)))") == -60
    assert calc.command("asindeg(-1)") == -90
    assert calc.command("cscdeg(-90)") == -1

    for d in range(-170, 171, 10):
        assert calc.command(f"asindeg({d}).evalf()") == calc.command(f"arcsindeg({d}).evalf()")
        assert calc.command(f"acosdeg({d}).evalf()") == calc.command(f"arccosdeg({d}).evalf()")
        assert calc.command(f"atandeg({d}).evalf()") == calc.command(f"arctandeg({d}).evalf()")
        assert calc.command(f"asecdeg({d}).evalf()") == calc.command(f"arcsecdeg({d}).evalf()")
        assert calc.command(f"acscdeg({d}).evalf()") == calc.command(f"arccscdeg({d}).evalf()")
        assert calc.command(f"atandeg({d}).evalf()") == calc.command(f"arctandeg({d}).evalf()")
