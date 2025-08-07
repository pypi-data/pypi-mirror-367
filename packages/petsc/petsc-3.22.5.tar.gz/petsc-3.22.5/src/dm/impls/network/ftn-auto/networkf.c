#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* network.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdmnetwork.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetplex_ DMNETWORKGETPLEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetplex_ dmnetworkgetplex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetnumsubnetworks_ DMNETWORKGETNUMSUBNETWORKS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetnumsubnetworks_ dmnetworkgetnumsubnetworks
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworksetnumsubnetworks_ DMNETWORKSETNUMSUBNETWORKS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworksetnumsubnetworks_ dmnetworksetnumsubnetworks
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkaddsubnetwork_ DMNETWORKADDSUBNETWORK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkaddsubnetwork_ dmnetworkaddsubnetwork
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworklayoutsetup_ DMNETWORKLAYOUTSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworklayoutsetup_ dmnetworklayoutsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkaddsharedvertices_ DMNETWORKADDSHAREDVERTICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkaddsharedvertices_ dmnetworkaddsharedvertices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetnumvertices_ DMNETWORKGETNUMVERTICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetnumvertices_ dmnetworkgetnumvertices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetnumedges_ DMNETWORKGETNUMEDGES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetnumedges_ dmnetworkgetnumedges
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetvertexrange_ DMNETWORKGETVERTEXRANGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetvertexrange_ dmnetworkgetvertexrange
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetedgerange_ DMNETWORKGETEDGERANGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetedgerange_ dmnetworkgetedgerange
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetglobaledgeindex_ DMNETWORKGETGLOBALEDGEINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetglobaledgeindex_ dmnetworkgetglobaledgeindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetglobalvertexindex_ DMNETWORKGETGLOBALVERTEXINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetglobalvertexindex_ dmnetworkgetglobalvertexindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetnumcomponents_ DMNETWORKGETNUMCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetnumcomponents_ dmnetworkgetnumcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetlocalvecoffset_ DMNETWORKGETLOCALVECOFFSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetlocalvecoffset_ dmnetworkgetlocalvecoffset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetglobalvecoffset_ DMNETWORKGETGLOBALVECOFFSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetglobalvecoffset_ dmnetworkgetglobalvecoffset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetedgeoffset_ DMNETWORKGETEDGEOFFSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetedgeoffset_ dmnetworkgetedgeoffset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetvertexoffset_ DMNETWORKGETVERTEXOFFSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetvertexoffset_ dmnetworkgetvertexoffset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkaddcomponent_ DMNETWORKADDCOMPONENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkaddcomponent_ dmnetworkaddcomponent
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetcomponent_ DMNETWORKGETCOMPONENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetcomponent_ dmnetworkgetcomponent
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkassemblegraphstructures_ DMNETWORKASSEMBLEGRAPHSTRUCTURES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkassemblegraphstructures_ dmnetworkassemblegraphstructures
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkdistribute_ DMNETWORKDISTRIBUTE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkdistribute_ dmnetworkdistribute
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfgetsubsf_ PETSCSFGETSUBSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfgetsubsf_ petscsfgetsubsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkissharedvertex_ DMNETWORKISSHAREDVERTEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkissharedvertex_ dmnetworkissharedvertex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkisghostvertex_ DMNETWORKISGHOSTVERTEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkisghostvertex_ dmnetworkisghostvertex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkhasjacobian_ DMNETWORKHASJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkhasjacobian_ dmnetworkhasjacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkedgesetmatrix_ DMNETWORKEDGESETMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkedgesetmatrix_ dmnetworkedgesetmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkvertexsetmatrix_ DMNETWORKVERTEXSETMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkvertexsetmatrix_ dmnetworkvertexsetmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkgetvertexlocaltoglobalordering_ DMNETWORKGETVERTEXLOCALTOGLOBALORDERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkgetvertexlocaltoglobalordering_ dmnetworkgetvertexlocaltoglobalordering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworksetvertexlocaltoglobalordering_ DMNETWORKSETVERTEXLOCALTOGLOBALORDERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworksetvertexlocaltoglobalordering_ dmnetworksetvertexlocaltoglobalordering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkcreateis_ DMNETWORKCREATEIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkcreateis_ dmnetworkcreateis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkcreatelocalis_ DMNETWORKCREATELOCALIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkcreatelocalis_ dmnetworkcreatelocalis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmnetworkfinalizecomponents_ DMNETWORKFINALIZECOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmnetworkfinalizecomponents_ dmnetworkfinalizecomponents
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmnetworkgetplex_(DM dm,DM *plexdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool plexdm_null = !*(void**) plexdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(plexdm);
*ierr = DMNetworkGetPlex(
	(DM)PetscToPointer((dm) ),plexdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! plexdm_null && !*(void**) plexdm) * (void **) plexdm = (void *)-2;
}
PETSC_EXTERN void  dmnetworkgetnumsubnetworks_(DM dm,PetscInt *nsubnet,PetscInt *Nsubnet, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(nsubnet);
CHKFORTRANNULLINTEGER(Nsubnet);
*ierr = DMNetworkGetNumSubNetworks(
	(DM)PetscToPointer((dm) ),nsubnet,Nsubnet);
}
PETSC_EXTERN void  dmnetworksetnumsubnetworks_(DM dm,PetscInt *nsubnet,PetscInt *Nsubnet, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMNetworkSetNumSubNetworks(
	(DM)PetscToPointer((dm) ),*nsubnet,*Nsubnet);
}
PETSC_EXTERN void  dmnetworkaddsubnetwork_(DM dm, char *name,PetscInt *ne,PetscInt edgelist[],PetscInt *netnum, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(edgelist);
CHKFORTRANNULLINTEGER(netnum);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMNetworkAddSubnetwork(
	(DM)PetscToPointer((dm) ),_cltmp0,*ne,edgelist,netnum);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmnetworklayoutsetup_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMNetworkLayoutSetUp(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmnetworkaddsharedvertices_(DM dm,PetscInt *anetnum,PetscInt *bnetnum,PetscInt *nsvtx,PetscInt asvtx[],PetscInt bsvtx[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(asvtx);
CHKFORTRANNULLINTEGER(bsvtx);
*ierr = DMNetworkAddSharedVertices(
	(DM)PetscToPointer((dm) ),*anetnum,*bnetnum,*nsvtx,asvtx,bsvtx);
}
PETSC_EXTERN void  dmnetworkgetnumvertices_(DM dm,PetscInt *nVertices,PetscInt *NVertices, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(nVertices);
CHKFORTRANNULLINTEGER(NVertices);
*ierr = DMNetworkGetNumVertices(
	(DM)PetscToPointer((dm) ),nVertices,NVertices);
}
PETSC_EXTERN void  dmnetworkgetnumedges_(DM dm,PetscInt *nEdges,PetscInt *NEdges, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(nEdges);
CHKFORTRANNULLINTEGER(NEdges);
*ierr = DMNetworkGetNumEdges(
	(DM)PetscToPointer((dm) ),nEdges,NEdges);
}
PETSC_EXTERN void  dmnetworkgetvertexrange_(DM dm,PetscInt *vStart,PetscInt *vEnd, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(vStart);
CHKFORTRANNULLINTEGER(vEnd);
*ierr = DMNetworkGetVertexRange(
	(DM)PetscToPointer((dm) ),vStart,vEnd);
}
PETSC_EXTERN void  dmnetworkgetedgerange_(DM dm,PetscInt *eStart,PetscInt *eEnd, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(eStart);
CHKFORTRANNULLINTEGER(eEnd);
*ierr = DMNetworkGetEdgeRange(
	(DM)PetscToPointer((dm) ),eStart,eEnd);
}
PETSC_EXTERN void  dmnetworkgetglobaledgeindex_(DM dm,PetscInt *p,PetscInt *index, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(index);
*ierr = DMNetworkGetGlobalEdgeIndex(
	(DM)PetscToPointer((dm) ),*p,index);
}
PETSC_EXTERN void  dmnetworkgetglobalvertexindex_(DM dm,PetscInt *p,PetscInt *index, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(index);
*ierr = DMNetworkGetGlobalVertexIndex(
	(DM)PetscToPointer((dm) ),*p,index);
}
PETSC_EXTERN void  dmnetworkgetnumcomponents_(DM dm,PetscInt *p,PetscInt *numcomponents, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(numcomponents);
*ierr = DMNetworkGetNumComponents(
	(DM)PetscToPointer((dm) ),*p,numcomponents);
}
PETSC_EXTERN void  dmnetworkgetlocalvecoffset_(DM dm,PetscInt *p,PetscInt *compnum,PetscInt *offset, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(offset);
*ierr = DMNetworkGetLocalVecOffset(
	(DM)PetscToPointer((dm) ),*p,*compnum,offset);
}
PETSC_EXTERN void  dmnetworkgetglobalvecoffset_(DM dm,PetscInt *p,PetscInt *compnum,PetscInt *offsetg, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(offsetg);
*ierr = DMNetworkGetGlobalVecOffset(
	(DM)PetscToPointer((dm) ),*p,*compnum,offsetg);
}
PETSC_EXTERN void  dmnetworkgetedgeoffset_(DM dm,PetscInt *p,PetscInt *offset, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(offset);
*ierr = DMNetworkGetEdgeOffset(
	(DM)PetscToPointer((dm) ),*p,offset);
}
PETSC_EXTERN void  dmnetworkgetvertexoffset_(DM dm,PetscInt *p,PetscInt *offset, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(offset);
*ierr = DMNetworkGetVertexOffset(
	(DM)PetscToPointer((dm) ),*p,offset);
}
PETSC_EXTERN void  dmnetworkaddcomponent_(DM dm,PetscInt *p,PetscInt *componentkey,void*compvalue,PetscInt *nvar, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMNetworkAddComponent(
	(DM)PetscToPointer((dm) ),*p,*componentkey,compvalue,*nvar);
}
PETSC_EXTERN void  dmnetworkgetcomponent_(DM dm,PetscInt *p,PetscInt *compnum,PetscInt *compkey,void**component,PetscInt *nvar, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(compkey);
CHKFORTRANNULLINTEGER(nvar);
*ierr = DMNetworkGetComponent(
	(DM)PetscToPointer((dm) ),*p,*compnum,compkey,component,nvar);
}
PETSC_EXTERN void  dmnetworkassemblegraphstructures_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMNetworkAssembleGraphStructures(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmnetworkdistribute_(DM *dm,PetscInt *overlap, int *ierr)
{
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMNetworkDistribute(dm,*overlap);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  petscsfgetsubsf_(PetscSF mainsf,ISLocalToGlobalMapping map,PetscSF *subSF, int *ierr)
{
CHKFORTRANNULLOBJECT(mainsf);
CHKFORTRANNULLOBJECT(map);
PetscBool subSF_null = !*(void**) subSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subSF);
*ierr = PetscSFGetSubSF(
	(PetscSF)PetscToPointer((mainsf) ),
	(ISLocalToGlobalMapping)PetscToPointer((map) ),subSF);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subSF_null && !*(void**) subSF) * (void **) subSF = (void *)-2;
}
PETSC_EXTERN void  dmnetworkissharedvertex_(DM dm,PetscInt *p,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMNetworkIsSharedVertex(
	(DM)PetscToPointer((dm) ),*p,flag);
}
PETSC_EXTERN void  dmnetworkisghostvertex_(DM dm,PetscInt *p,PetscBool *isghost, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMNetworkIsGhostVertex(
	(DM)PetscToPointer((dm) ),*p,isghost);
}
PETSC_EXTERN void  dmnetworkhasjacobian_(DM dm,PetscBool *eflg,PetscBool *vflg, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMNetworkHasJacobian(
	(DM)PetscToPointer((dm) ),*eflg,*vflg);
}
PETSC_EXTERN void  dmnetworkedgesetmatrix_(DM dm,PetscInt *p,Mat J[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool J_null = !*(void**) J ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(J);
*ierr = DMNetworkEdgeSetMatrix(
	(DM)PetscToPointer((dm) ),*p,J);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! J_null && !*(void**) J) * (void **) J = (void *)-2;
}
PETSC_EXTERN void  dmnetworkvertexsetmatrix_(DM dm,PetscInt *p,Mat J[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool J_null = !*(void**) J ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(J);
*ierr = DMNetworkVertexSetMatrix(
	(DM)PetscToPointer((dm) ),*p,J);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! J_null && !*(void**) J) * (void **) J = (void *)-2;
}
PETSC_EXTERN void  dmnetworkgetvertexlocaltoglobalordering_(DM dm,PetscInt *vloc,PetscInt *vg, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(vg);
*ierr = DMNetworkGetVertexLocalToGlobalOrdering(
	(DM)PetscToPointer((dm) ),*vloc,vg);
}
PETSC_EXTERN void  dmnetworksetvertexlocaltoglobalordering_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMNetworkSetVertexLocalToGlobalOrdering(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmnetworkcreateis_(DM dm,PetscInt *numkeys,PetscInt keys[],PetscInt blocksize[],PetscInt nselectedvar[],PetscInt *selectedvar[],IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(keys);
CHKFORTRANNULLINTEGER(blocksize);
CHKFORTRANNULLINTEGER(nselectedvar);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = DMNetworkCreateIS(
	(DM)PetscToPointer((dm) ),*numkeys,keys,blocksize,nselectedvar,selectedvar,is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  dmnetworkcreatelocalis_(DM dm,PetscInt *numkeys,PetscInt keys[],PetscInt blocksize[],PetscInt nselectedvar[],PetscInt *selectedvar[],IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(keys);
CHKFORTRANNULLINTEGER(blocksize);
CHKFORTRANNULLINTEGER(nselectedvar);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = DMNetworkCreateLocalIS(
	(DM)PetscToPointer((dm) ),*numkeys,keys,blocksize,nselectedvar,selectedvar,is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  dmnetworkfinalizecomponents_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMNetworkFinalizeComponents(
	(DM)PetscToPointer((dm) ));
}
#if defined(__cplusplus)
}
#endif
