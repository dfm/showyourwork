from showyourwork import paths, test_util

plugin_id = "showyourwork.plugins.tex"


def test_basic() -> None:
    with test_util.temporary_project() as d:
        p = paths.work({"working_directory": d})
        open(p.manuscript, "w").write(
            r"""
\documentclass{article}
\usepackage{showyourwork}
\begin{document}
Test.
\end{document}
            """
        )
        test_util.run_snakemake(
            str(paths.package_data(plugin_id, "workflow", "Snakefile")),
            ["_syw_plug_tex_xml_tree", "--config", f"working_directory={d}"],
            cwd=d,
        )
        assert (p.plugin(plugin_id, "xml") / "showyourwork.xml").is_file()


def test_figure() -> None:
    with test_util.temporary_project() as d:
        p = paths.work({"working_directory": d})
        open(p.manuscript, "w").write(
            r"""
\documentclass{article}
\usepackage{showyourwork}
\begin{document}
Test.
\begin{figure}
\includegraphics{test.png}
\end{figure}
\end{document}
            """
        )
        test_util.run_snakemake(
            str(paths.package_data(plugin_id, "workflow", "Snakefile")),
            ["_syw_plug_tex_xml_tree", "--config", f"working_directory={d}"],
            cwd=d,
        )
        xml_tree = p.plugin(plugin_id, "xml") / "showyourwork.xml"
        assert xml_tree.is_file()
        assert (
            xml_tree.read_text()
            == """<!--XML article tree automatically generated by showyourwork-->
<FIGURE>
<GRAPHICS>test.png</GRAPHICS>
</FIGURE>
"""
        )