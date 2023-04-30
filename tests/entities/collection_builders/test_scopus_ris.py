import io

from bibx import read_scopus_ris


def test_scopus_works():
    file = io.StringIO(
        """
TY  - JOUR
TI  - FORC signatures and switching-field distributions of dipolar coupled nanowire-based hysterons
T2  - Journal of Applied Physics
J2  - J Appl Phys
VL  - 128
IS  - 9
PY  - 2020
DO  - 10.1063/5.0020407
AU  - Pierrot, A.
AU  - Béron, F.
AU  - Blon, T.
N1  - Export Date: 15 October 2020
M3  - Article
DB  - Scopus
C7  - 093903
N1  - References: Mayergoyz, I.D., (1986) Phys. Rev. Lett., 56, p. 1518;
Preisach, F., (1935) Z. Phys., 94, p. 277;
Roberts, A.P., Heslop, D., Zhao, X., Pike, C.R., (2014) Rev. Geophys., 52, pp. 557-602. , https://doi.org/10.1002/2014RG000462;
Pike, C.R., Roberts, A.P., Verosub, K.L., (1999) J. Appl. Phys., 85, p. 6660;
Dobrot, C.-I., Stancu, A., (2013) J. Appl. Phys., 113;
Carvallo, C., Muxworthy, A., (2006) Geochem. Geophys. Geosyst., 7, p. Q09003. , https://doi.org/10.1029/2006GC001299;
Lappe, S.-C.L.L., Feinberg, J.M., Muxworthy, A., Harrison, R.J., (2013) Geochem. Geophys. Geosyst., 14, p. 2143. , https://doi.org/10.1002/ggge.20141;
Zhao, X., Roberts, A.P., Heslop, D., Paterson, G.A., Li, Y., Li, J., (2017) J. Geophys. Res. Solid Earth, 122, p. 4767. , https://doi.org/10.1002/2016JB013683;
Papusoi, C., Srinivasan, K., Acharya, R., (2011) J. Appl. Phys., 110;
Papusoi, C., Desai, M., Acharya, R., (2015) J. Phys. D Appl. Phys., 48;
UR  - https://www.scopus.com/inward/record.uri?eid=2-s2.0-85091557653&doi=10.1063%2f5.0020407&partnerID=40&md5=1471f5e876fae65e040690b345036add
ER  -
"""
    )
    data = read_scopus_ris(file)
    assert len(data.articles) == 1
    (article,) = data.articles
    assert (
        article.title
        == "FORC signatures and switching-field distributions of dipolar coupled nanowire-based hysterons"
    )
    assert article.year == 2020
    assert len(list(data.citation_pairs)) == 10
