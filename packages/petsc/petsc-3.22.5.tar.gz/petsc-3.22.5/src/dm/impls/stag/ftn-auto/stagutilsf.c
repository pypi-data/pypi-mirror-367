#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* stagutils.c */
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

#include "petscdmstag.h"
#include "petscdmproduct.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetcorners_ DMSTAGGETCORNERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetcorners_ dmstaggetcorners
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetdof_ DMSTAGGETDOF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetdof_ dmstaggetdof
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetghostcorners_ DMSTAGGETGHOSTCORNERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetghostcorners_ dmstaggetghostcorners
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetglobalsizes_ DMSTAGGETGLOBALSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetglobalsizes_ dmstaggetglobalsizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetlocalsizes_ DMSTAGGETLOCALSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetlocalsizes_ dmstaggetlocalsizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetnumranks_ DMSTAGGETNUMRANKS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetnumranks_ dmstaggetnumranks
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetentries_ DMSTAGGETENTRIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetentries_ dmstaggetentries
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetentrieslocal_ DMSTAGGETENTRIESLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetentrieslocal_ dmstaggetentrieslocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetentriesperelement_ DMSTAGGETENTRIESPERELEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetentriesperelement_ dmstaggetentriesperelement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetstenciltype_ DMSTAGGETSTENCILTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetstenciltype_ dmstaggetstenciltype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetstencilwidth_ DMSTAGGETSTENCILWIDTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetstencilwidth_ dmstaggetstencilwidth
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagcreatecompatibledmstag_ DMSTAGCREATECOMPATIBLEDMSTAG
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagcreatecompatibledmstag_ dmstagcreatecompatibledmstag
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetlocationslot_ DMSTAGGETLOCATIONSLOT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetlocationslot_ dmstaggetlocationslot
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstaggetrefinementfactor_ DMSTAGGETREFINEMENTFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstaggetrefinementfactor_ dmstaggetrefinementfactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagmigratevec_ DMSTAGMIGRATEVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagmigratevec_ dmstagmigratevec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagpopulatelocaltoglobalinjective_ DMSTAGPOPULATELOCALTOGLOBALINJECTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagpopulatelocaltoglobalinjective_ dmstagpopulatelocaltoglobalinjective
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetboundarytypes_ DMSTAGSETBOUNDARYTYPES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetboundarytypes_ dmstagsetboundarytypes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetdof_ DMSTAGSETDOF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetdof_ dmstagsetdof
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetnumranks_ DMSTAGSETNUMRANKS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetnumranks_ dmstagsetnumranks
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetstenciltype_ DMSTAGSETSTENCILTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetstenciltype_ dmstagsetstenciltype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetstencilwidth_ DMSTAGSETSTENCILWIDTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetstencilwidth_ dmstagsetstencilwidth
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetglobalsizes_ DMSTAGSETGLOBALSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetglobalsizes_ dmstagsetglobalsizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetownershipranges_ DMSTAGSETOWNERSHIPRANGES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetownershipranges_ dmstagsetownershipranges
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetrefinementfactor_ DMSTAGSETREFINEMENTFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetrefinementfactor_ dmstagsetrefinementfactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetuniformcoordinates_ DMSTAGSETUNIFORMCOORDINATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetuniformcoordinates_ dmstagsetuniformcoordinates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetuniformcoordinatesexplicit_ DMSTAGSETUNIFORMCOORDINATESEXPLICIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetuniformcoordinatesexplicit_ dmstagsetuniformcoordinatesexplicit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagsetuniformcoordinatesproduct_ DMSTAGSETUNIFORMCOORDINATESPRODUCT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagsetuniformcoordinatesproduct_ dmstagsetuniformcoordinatesproduct
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmstaggetcorners_(DM dm,PetscInt *x,PetscInt *y,PetscInt *z,PetscInt *m,PetscInt *n,PetscInt *p,PetscInt *nExtrax,PetscInt *nExtray,PetscInt *nExtraz, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(x);
CHKFORTRANNULLINTEGER(y);
CHKFORTRANNULLINTEGER(z);
CHKFORTRANNULLINTEGER(m);
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLINTEGER(p);
CHKFORTRANNULLINTEGER(nExtrax);
CHKFORTRANNULLINTEGER(nExtray);
CHKFORTRANNULLINTEGER(nExtraz);
*ierr = DMStagGetCorners(
	(DM)PetscToPointer((dm) ),x,y,z,m,n,p,nExtrax,nExtray,nExtraz);
}
PETSC_EXTERN void  dmstaggetdof_(DM dm,PetscInt *dof0,PetscInt *dof1,PetscInt *dof2,PetscInt *dof3, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(dof0);
CHKFORTRANNULLINTEGER(dof1);
CHKFORTRANNULLINTEGER(dof2);
CHKFORTRANNULLINTEGER(dof3);
*ierr = DMStagGetDOF(
	(DM)PetscToPointer((dm) ),dof0,dof1,dof2,dof3);
}
PETSC_EXTERN void  dmstaggetghostcorners_(DM dm,PetscInt *x,PetscInt *y,PetscInt *z,PetscInt *m,PetscInt *n,PetscInt *p, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(x);
CHKFORTRANNULLINTEGER(y);
CHKFORTRANNULLINTEGER(z);
CHKFORTRANNULLINTEGER(m);
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLINTEGER(p);
*ierr = DMStagGetGhostCorners(
	(DM)PetscToPointer((dm) ),x,y,z,m,n,p);
}
PETSC_EXTERN void  dmstaggetglobalsizes_(DM dm,PetscInt *M,PetscInt *N,PetscInt *P, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(M);
CHKFORTRANNULLINTEGER(N);
CHKFORTRANNULLINTEGER(P);
*ierr = DMStagGetGlobalSizes(
	(DM)PetscToPointer((dm) ),M,N,P);
}
PETSC_EXTERN void  dmstaggetlocalsizes_(DM dm,PetscInt *m,PetscInt *n,PetscInt *p, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(m);
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLINTEGER(p);
*ierr = DMStagGetLocalSizes(
	(DM)PetscToPointer((dm) ),m,n,p);
}
PETSC_EXTERN void  dmstaggetnumranks_(DM dm,PetscInt *nRanks0,PetscInt *nRanks1,PetscInt *nRanks2, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(nRanks0);
CHKFORTRANNULLINTEGER(nRanks1);
CHKFORTRANNULLINTEGER(nRanks2);
*ierr = DMStagGetNumRanks(
	(DM)PetscToPointer((dm) ),nRanks0,nRanks1,nRanks2);
}
PETSC_EXTERN void  dmstaggetentries_(DM dm,PetscInt *entries, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(entries);
*ierr = DMStagGetEntries(
	(DM)PetscToPointer((dm) ),entries);
}
PETSC_EXTERN void  dmstaggetentrieslocal_(DM dm,PetscInt *entries, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(entries);
*ierr = DMStagGetEntriesLocal(
	(DM)PetscToPointer((dm) ),entries);
}
PETSC_EXTERN void  dmstaggetentriesperelement_(DM dm,PetscInt *entriesPerElement, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(entriesPerElement);
*ierr = DMStagGetEntriesPerElement(
	(DM)PetscToPointer((dm) ),entriesPerElement);
}
PETSC_EXTERN void  dmstaggetstenciltype_(DM dm,DMStagStencilType *stencilType, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagGetStencilType(
	(DM)PetscToPointer((dm) ),stencilType);
}
PETSC_EXTERN void  dmstaggetstencilwidth_(DM dm,PetscInt *stencilWidth, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(stencilWidth);
*ierr = DMStagGetStencilWidth(
	(DM)PetscToPointer((dm) ),stencilWidth);
}
PETSC_EXTERN void  dmstagcreatecompatibledmstag_(DM dm,PetscInt *dof0,PetscInt *dof1,PetscInt *dof2,PetscInt *dof3,DM *newdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool newdm_null = !*(void**) newdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newdm);
*ierr = DMStagCreateCompatibleDMStag(
	(DM)PetscToPointer((dm) ),*dof0,*dof1,*dof2,*dof3,newdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newdm_null && !*(void**) newdm) * (void **) newdm = (void *)-2;
}
PETSC_EXTERN void  dmstaggetlocationslot_(DM dm,DMStagStencilLocation *loc,PetscInt *c,PetscInt *slot, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(slot);
*ierr = DMStagGetLocationSlot(
	(DM)PetscToPointer((dm) ),*loc,*c,slot);
}
PETSC_EXTERN void  dmstaggetrefinementfactor_(DM dm,PetscInt *refine_x,PetscInt *refine_y,PetscInt *refine_z, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(refine_x);
CHKFORTRANNULLINTEGER(refine_y);
CHKFORTRANNULLINTEGER(refine_z);
*ierr = DMStagGetRefinementFactor(
	(DM)PetscToPointer((dm) ),refine_x,refine_y,refine_z);
}
PETSC_EXTERN void  dmstagmigratevec_(DM dm,Vec vec,DM dmTo,Vec vecTo, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(vec);
CHKFORTRANNULLOBJECT(dmTo);
CHKFORTRANNULLOBJECT(vecTo);
*ierr = DMStagMigrateVec(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((vec) ),
	(DM)PetscToPointer((dmTo) ),
	(Vec)PetscToPointer((vecTo) ));
}
PETSC_EXTERN void  dmstagpopulatelocaltoglobalinjective_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagPopulateLocalToGlobalInjective(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmstagsetboundarytypes_(DM dm,DMBoundaryType *boundaryType0,DMBoundaryType *boundaryType1,DMBoundaryType *boundaryType2, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagSetBoundaryTypes(
	(DM)PetscToPointer((dm) ),*boundaryType0,*boundaryType1,*boundaryType2);
}
PETSC_EXTERN void  dmstagsetdof_(DM dm,PetscInt *dof0,PetscInt *dof1,PetscInt *dof2,PetscInt *dof3, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagSetDOF(
	(DM)PetscToPointer((dm) ),*dof0,*dof1,*dof2,*dof3);
}
PETSC_EXTERN void  dmstagsetnumranks_(DM dm,PetscInt *nRanks0,PetscInt *nRanks1,PetscInt *nRanks2, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagSetNumRanks(
	(DM)PetscToPointer((dm) ),*nRanks0,*nRanks1,*nRanks2);
}
PETSC_EXTERN void  dmstagsetstenciltype_(DM dm,DMStagStencilType *stencilType, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagSetStencilType(
	(DM)PetscToPointer((dm) ),*stencilType);
}
PETSC_EXTERN void  dmstagsetstencilwidth_(DM dm,PetscInt *stencilWidth, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagSetStencilWidth(
	(DM)PetscToPointer((dm) ),*stencilWidth);
}
PETSC_EXTERN void  dmstagsetglobalsizes_(DM dm,PetscInt *N0,PetscInt *N1,PetscInt *N2, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagSetGlobalSizes(
	(DM)PetscToPointer((dm) ),*N0,*N1,*N2);
}
PETSC_EXTERN void  dmstagsetownershipranges_(DM dm, PetscInt lx[], PetscInt ly[], PetscInt lz[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(lx);
CHKFORTRANNULLINTEGER(ly);
CHKFORTRANNULLINTEGER(lz);
*ierr = DMStagSetOwnershipRanges(
	(DM)PetscToPointer((dm) ),lx,ly,lz);
}
PETSC_EXTERN void  dmstagsetrefinementfactor_(DM dm,PetscInt *refine_x,PetscInt *refine_y,PetscInt *refine_z, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagSetRefinementFactor(
	(DM)PetscToPointer((dm) ),*refine_x,*refine_y,*refine_z);
}
PETSC_EXTERN void  dmstagsetuniformcoordinates_(DM dm,PetscReal *xmin,PetscReal *xmax,PetscReal *ymin,PetscReal *ymax,PetscReal *zmin,PetscReal *zmax, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagSetUniformCoordinates(
	(DM)PetscToPointer((dm) ),*xmin,*xmax,*ymin,*ymax,*zmin,*zmax);
}
PETSC_EXTERN void  dmstagsetuniformcoordinatesexplicit_(DM dm,PetscReal *xmin,PetscReal *xmax,PetscReal *ymin,PetscReal *ymax,PetscReal *zmin,PetscReal *zmax, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagSetUniformCoordinatesExplicit(
	(DM)PetscToPointer((dm) ),*xmin,*xmax,*ymin,*ymax,*zmin,*zmax);
}
PETSC_EXTERN void  dmstagsetuniformcoordinatesproduct_(DM dm,PetscReal *xmin,PetscReal *xmax,PetscReal *ymin,PetscReal *ymax,PetscReal *zmin,PetscReal *zmax, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagSetUniformCoordinatesProduct(
	(DM)PetscToPointer((dm) ),*xmin,*xmax,*ymin,*ymax,*zmin,*zmax);
}
#if defined(__cplusplus)
}
#endif
