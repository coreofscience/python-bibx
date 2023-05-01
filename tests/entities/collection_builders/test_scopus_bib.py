import io

from bibx import read_scopus_bib


def test_scopus_works():
    file = io.StringIO(
        """
@ARTICLE{Steblinski2022,
author={Steblinski, P. and Blachowicz, T. and Ehrmann, A.},
title={Analysis of the energy distribution of iron nano-spheres for bit-patterned media},
journal={Journal of Magnetism and Magnetic Materials},
year={2022},
volume={562},
doi={10.1016/j.jmmm.2022.169805},
art_number={169805},
note={cited By 0},
url={https://www.scopus.com/inward/record.uri?eid=2-s2.0-85135886322&doi=10.1016%2fj.jmmm.2022.169805&partnerID=40&md5=759122e06fc4fd8cc4a87011561de73b},
affiliation={Koszalin University of Technology, Faculty of Electronics and Informatics, Koszalin, Poland; Silesian University of Technology, Institute of Physics – Center for Science and Education, Gliwice, Poland; Bielefeld University of Applied Sciences, Faculty of Engineering Sciences and Mathematics, Bielefeld, Germany},
abstract={Improved magnetic memory systems belong to the main research topics in spintronics. Here we show micromagnetic simulations used to analyze the energy density of nano-scaled iron spheres. Layers of different thickness, partly coated with iron oxide, were tested in terms of spatial uniformity of the physical system energy. For a single non-coated or iron-oxide coated droplet, the spatial distribution of the total energy is not uniform and depends on the nano-droplet size. Additionally, for systems consisting of four objects, the relation between relative distance and the resultant magnetization distribution was analyzed. The mutual relation between droplet size and the underlying magnetization distribution as well as the character of local energy extrema was investigated. The size changes for the four-droplet system were compared with the single object behavior to obtain a criterion for the minimum distance between spheres to behave as a single object. The calculations revealed that the oxidized spheres could be placed closer to each other in comparison to the non-coated system. For the proposed oxide coated system, the increase of this maximum packing density is equal to about 12%, as compared to the non-coated system. © 2022 Elsevier B.V.},
author_keywords={Ferromagnetism;  Magnetic anisotropy;  Micromagnetism},
keywords={Drops;  Ferromagnetic materials;  Ferromagnetism;  Magnetic anisotropy;  Magnetic storage;  Magnetization;  Spheres, Bit-patterned media;  Coated systems;  Droplets sizes;  Energy distributions;  Magnetic memory;  Magnetization distribution;  Memory systems;  Micromagnetisms;  Nano-spheres;  Single object, Iron oxides},
references={Richter, H., Dobin, A., Heinonen, O., Gao, K., Veerdonk, R., Lynch, R., Xue, J., Brockie, R., Recording on Bit-Patterned Media at Densities of 1 Tb/in and Beyond (2006) IEEE Trans. Magn., 42, pp. 2255-2260; Koltsov, D.K., Adeyeye, A.O., Welland, M.E., Tricker, D.M., Single-domain circular nanomagnets (1999) Phys. Rev. Lett., 83, p. 1042; Zhang, W., Haas, S., Phase diagram of magnetization reversal processes in nanorings (2010) Phys. Rev. B, 81; He, K., Smith, D.J., McCartney, M.R., Effects of vortex chirality and shape anisotropy on magnetization reversal of Co nanorings (invited) (2010) J. Appl. Phys., 107, p. 09D307; Blachowicz, T., Ehrmann, A., Square nano-magnets as bit-patterned media with doubled possible data density (2017) Mater. Today:. Proc., 4, pp. S226-S231; Döpke, C., Grothe, T., Steblinski, P., Klöcker, M., Sabantina, L., Kosmalska, D., Blachowicz, T., Ehrmann, A., Magnetic Nanofiber Mats for Data Storage and Transfer (2019) Nanomaterials, 9, p. 92; Steblinski, P., Blachowicz, T., Conception of magnetic memory switched by time dependent current density and current electron spin polarization (2019) International Journal of Electronics and Telecommunications, 65, p. 309; Shutyi, A.M., Sementsov, D.I., Multistability of the Magnetization Reversal of a Nanoparticle with Cubic Anisotropy (2020) JETP Lett., 111, pp. 619-626; Russier, V., De-Montferrand, C., Lalatonne, Y., Motte, L., Magnetization of densely packed interacting magnetic nanoparticles with cubic and uniaxial anisotropies: a Monte Carlo study (2013) J. Appl. Phys., 114; Simeonidis, K., Martinez-Boubeta, C., Serantes, D., Ruta, S., Chubykalo-Fesenko, O., Chantrell, R., Oró-Solé, J., Angelakeris, M., Controlling Magnetization Reversal and Hyperthermia Efficiency in Core−Shell Iron−Iron Oxide Magnetic Nanoparticles by Tuning the Interphase Coupling (2020) ACS Appl. Nano Mater., 3, p. 4465; Nemati, Z., Alonso, J., Khurshid, H., Phan, M.H., Srikanth, H., Core/shell iron/iron oxide nanoparticles: are they promising for magnetic hyperthermia? (2016) RSC Adv., 6, p. 38697; Kim, Y.-W., Park, H.S., Hyun Soon Park Microstructural and Magnetic Characterization of Iron Oxide Nanoparticles Fabricated by Pulsed Wire Evaporation (2019) Electron. Mater. Lett., 15 (6), pp. 665-672; Scholz, W., Fidler, J., Schrefl, T., Suess, D., Dittrich, R., Forster, H., Tsiantos, V., Scalable parallel micromagnetic solvers for magnetic nanostructures (2003) Comput. Mater. Sci., 28, p. 366; (2019), TAO Users Manual, ANL/MCS-TM-322 Rev. 3.11, Argonne National Laboratory; Kostopoulou, A., Brintakis, K., Vasilakaki, M., Trohidou, K.N., Douvalis, A.P., Lascialfari, A., Manna, L., Lappas, A., Assembly-mediated Interplay of Dipolar Interactions and Surface Spin Disorder in Colloidal Maghemite Nanoclusters (2014) Nanoscale, 6 (7), pp. 3764-3776; Coey, J.M.D., Magnetism and Magnetic Materials (2010), Cambridge University Press; Cullity, B.D., Graham, C.D., Introduction to magnetic materials (2008), 2nd ed. Wiley; Johansson, C., Hanson, M., Pedersen, M.S., Morup, S., Magnetic properties of magnetic liquids with iron-oxide particles—the influence of anisotropy and interactions (1997) J. Magn. Magn. Mater., 173, pp. 5-14; Aguilera-del-Toro, R.H., Aguilera-Granja, F., Torres, M.B., Vega, A., Relation between structural patterns and magnetism in small iron oxide clusters: reentrance of the magnetic moment at high oxidation ratios (2021) Phys. Chem. Chem. Phys., 23, pp. 246-272; Erlebach, A., Hühn, C., Jana, R., Sierka, M., Structure and magnetic properties of (Fe2O3)n clusters (n = 1–5) (2014) Phys. Chem. Chem. Phys., 16 (48), pp. 26421-26426},
correspondence_address1={Blachowicz, T.; Silesian University of Technology, S. Konarskiego 22B str., 44-100 Gliwice, Poland; email: tomasz.blachowicz@polsl.pl},
publisher={Elsevier B.V.},
issn={03048853},
coden={JMMMD},
language={English},
abbrev_source_title={J Magn Magn Mater},
document_type={Article},
source={Scopus},
}
"""
    )
    data = read_scopus_bib(file)
    assert len(data.articles) == 1
    (article,) = data.articles
    assert (
        article.title
        == "Analysis of the energy distribution of iron nano-spheres for bit-patterned media"
    )
    assert len(list(data.citation_pairs)) == 20
