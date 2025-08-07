#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plex.c */
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

#include "petscdmplex.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexissimplex_ DMPLEXISSIMPLEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexissimplex_ dmplexissimplex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetsimplexorboxcells_ DMPLEXGETSIMPLEXORBOXCELLS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetsimplexorboxcells_ dmplexgetsimplexorboxcells
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexvecview1d_ DMPLEXVECVIEW1D
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexvecview1d_ dmplexvecview1d
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextopologyview_ DMPLEXTOPOLOGYVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextopologyview_ dmplextopologyview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcoordinatesview_ DMPLEXCOORDINATESVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcoordinatesview_ dmplexcoordinatesview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexlabelsview_ DMPLEXLABELSVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexlabelsview_ dmplexlabelsview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsectionview_ DMPLEXSECTIONVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsectionview_ dmplexsectionview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexglobalvectorview_ DMPLEXGLOBALVECTORVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexglobalvectorview_ dmplexglobalvectorview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexlocalvectorview_ DMPLEXLOCALVECTORVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexlocalvectorview_ dmplexlocalvectorview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextopologyload_ DMPLEXTOPOLOGYLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextopologyload_ dmplextopologyload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcoordinatesload_ DMPLEXCOORDINATESLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcoordinatesload_ dmplexcoordinatesload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexlabelsload_ DMPLEXLABELSLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexlabelsload_ dmplexlabelsload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsectionload_ DMPLEXSECTIONLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsectionload_ dmplexsectionload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexglobalvectorload_ DMPLEXGLOBALVECTORLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexglobalvectorload_ dmplexglobalvectorload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexlocalvectorload_ DMPLEXLOCALVECTORLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexlocalvectorload_ dmplexlocalvectorload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetsubdomainsection_ DMPLEXGETSUBDOMAINSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetsubdomainsection_ dmplexgetsubdomainsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetchart_ DMPLEXGETCHART
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetchart_ dmplexgetchart
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetchart_ DMPLEXSETCHART
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetchart_ dmplexsetchart
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetconesize_ DMPLEXGETCONESIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetconesize_ dmplexgetconesize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetconesize_ DMPLEXSETCONESIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetconesize_ dmplexsetconesize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetconetuple_ DMPLEXGETCONETUPLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetconetuple_ dmplexgetconetuple
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetconerecursivevertices_ DMPLEXGETCONERECURSIVEVERTICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetconerecursivevertices_ dmplexgetconerecursivevertices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetconerecursive_ DMPLEXGETCONERECURSIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetconerecursive_ dmplexgetconerecursive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexrestoreconerecursive_ DMPLEXRESTORECONERECURSIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexrestoreconerecursive_ dmplexrestoreconerecursive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetcone_ DMPLEXSETCONE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetcone_ dmplexsetcone
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetconeorientation_ DMPLEXSETCONEORIENTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetconeorientation_ dmplexsetconeorientation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexinsertcone_ DMPLEXINSERTCONE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexinsertcone_ dmplexinsertcone
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexinsertconeorientation_ DMPLEXINSERTCONEORIENTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexinsertconeorientation_ dmplexinsertconeorientation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetsupportsize_ DMPLEXGETSUPPORTSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetsupportsize_ dmplexgetsupportsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetsupportsize_ DMPLEXSETSUPPORTSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetsupportsize_ dmplexsetsupportsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetsupport_ DMPLEXSETSUPPORT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetsupport_ dmplexsetsupport
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexinsertsupport_ DMPLEXINSERTSUPPORT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexinsertsupport_ dmplexinsertsupport
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetmaxsizes_ DMPLEXGETMAXSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetmaxsizes_ dmplexgetmaxsizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsymmetrize_ DMPLEXSYMMETRIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsymmetrize_ dmplexsymmetrize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexstratify_ DMPLEXSTRATIFY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexstratify_ dmplexstratify
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputecelltypes_ DMPLEXCOMPUTECELLTYPES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputecelltypes_ dmplexcomputecelltypes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexequal_ DMPLEXEQUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexequal_ dmplexequal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetnumfacevertices_ DMPLEXGETNUMFACEVERTICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetnumfacevertices_ dmplexgetnumfacevertices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetdepthlabel_ DMPLEXGETDEPTHLABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetdepthlabel_ dmplexgetdepthlabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetdepth_ DMPLEXGETDEPTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetdepth_ dmplexgetdepth
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetdepthstratum_ DMPLEXGETDEPTHSTRATUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetdepthstratum_ dmplexgetdepthstratum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetheightstratum_ DMPLEXGETHEIGHTSTRATUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetheightstratum_ dmplexgetheightstratum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetpointdepth_ DMPLEXGETPOINTDEPTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetpointdepth_ dmplexgetpointdepth
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetpointheight_ DMPLEXGETPOINTHEIGHT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetpointheight_ dmplexgetpointheight
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetcelltypelabel_ DMPLEXGETCELLTYPELABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetcelltypelabel_ dmplexgetcelltypelabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetcelltype_ DMPLEXGETCELLTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetcelltype_ dmplexgetcelltype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetcelltype_ DMPLEXSETCELLTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetcelltype_ dmplexsetcelltype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetconesection_ DMPLEXGETCONESECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetconesection_ dmplexgetconesection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetsupportsection_ DMPLEXGETSUPPORTSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetsupportsection_ dmplexgetsupportsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetclosurepermutationtensor_ DMPLEXSETCLOSUREPERMUTATIONTENSOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetclosurepermutationtensor_ dmplexsetclosurepermutationtensor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetvtkcellheight_ DMPLEXGETVTKCELLHEIGHT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetvtkcellheight_ dmplexgetvtkcellheight
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetvtkcellheight_ DMPLEXSETVTKCELLHEIGHT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetvtkcellheight_ dmplexsetvtkcellheight
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetcelltypestratum_ DMPLEXGETCELLTYPESTRATUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetcelltypestratum_ dmplexgetcelltypestratum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetdepthstratumglobalsize_ DMPLEXGETDEPTHSTRATUMGLOBALSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetdepthstratumglobalsize_ dmplexgetdepthstratumglobalsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatecellnumbering_ DMPLEXCREATECELLNUMBERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatecellnumbering_ dmplexcreatecellnumbering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetcellnumbering_ DMPLEXGETCELLNUMBERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetcellnumbering_ dmplexgetcellnumbering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetvertexnumbering_ DMPLEXGETVERTEXNUMBERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetvertexnumbering_ dmplexgetvertexnumbering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatepointnumbering_ DMPLEXCREATEPOINTNUMBERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatepointnumbering_ dmplexcreatepointnumbering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreateedgenumbering_ DMPLEXCREATEEDGENUMBERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreateedgenumbering_ dmplexcreateedgenumbering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreaterankfield_ DMPLEXCREATERANKFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreaterankfield_ dmplexcreaterankfield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatelabelfield_ DMPLEXCREATELABELFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatelabelfield_ dmplexcreatelabelfield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexchecksymmetry_ DMPLEXCHECKSYMMETRY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexchecksymmetry_ dmplexchecksymmetry
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcheckskeleton_ DMPLEXCHECKSKELETON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcheckskeleton_ dmplexcheckskeleton
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcheckfaces_ DMPLEXCHECKFACES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcheckfaces_ dmplexcheckfaces
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcheckgeometry_ DMPLEXCHECKGEOMETRY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcheckgeometry_ dmplexcheckgeometry
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcheckpointsf_ DMPLEXCHECKPOINTSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcheckpointsf_ dmplexcheckpointsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcheckorphanvertices_ DMPLEXCHECKORPHANVERTICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcheckorphanvertices_ dmplexcheckorphanvertices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcheck_ DMPLEXCHECK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcheck_ dmplexcheck
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcheckcellshape_ DMPLEXCHECKCELLSHAPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcheckcellshape_ dmplexcheckcellshape
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputeorthogonalquality_ DMPLEXCOMPUTEORTHOGONALQUALITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputeorthogonalquality_ dmplexcomputeorthogonalquality
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetregularrefinement_ DMPLEXGETREGULARREFINEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetregularrefinement_ dmplexgetregularrefinement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetregularrefinement_ DMPLEXSETREGULARREFINEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetregularrefinement_ dmplexsetregularrefinement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetanchors_ DMPLEXGETANCHORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetanchors_ dmplexgetanchors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetanchors_ DMPLEXSETANCHORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetanchors_ dmplexsetanchors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexmonitorthroughput_ DMPLEXMONITORTHROUGHPUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexmonitorthroughput_ dmplexmonitorthroughput
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexissimplex_(DM dm,PetscBool *simplex, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexIsSimplex(
	(DM)PetscToPointer((dm) ),simplex);
}
PETSC_EXTERN void  dmplexgetsimplexorboxcells_(DM dm,PetscInt *height,PetscInt *cStart,PetscInt *cEnd, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(cStart);
CHKFORTRANNULLINTEGER(cEnd);
*ierr = DMPlexGetSimplexOrBoxCells(
	(DM)PetscToPointer((dm) ),*height,cStart,cEnd);
}
PETSC_EXTERN void  dmplexvecview1d_(DM dm,PetscInt *n,Vec u[],PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool u_null = !*(void**) u ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(u);
CHKFORTRANNULLOBJECT(viewer);
*ierr = DMPlexVecView1D(
	(DM)PetscToPointer((dm) ),*n,u,PetscPatchDefaultViewers((PetscViewer*)viewer));
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! u_null && !*(void**) u) * (void **) u = (void *)-2;
}
PETSC_EXTERN void  dmplextopologyview_(DM dm,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
*ierr = DMPlexTopologyView(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  dmplexcoordinatesview_(DM dm,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
*ierr = DMPlexCoordinatesView(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  dmplexlabelsview_(DM dm,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
*ierr = DMPlexLabelsView(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  dmplexsectionview_(DM dm,PetscViewer viewer,DM sectiondm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLOBJECT(sectiondm);
*ierr = DMPlexSectionView(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),
	(DM)PetscToPointer((sectiondm) ));
}
PETSC_EXTERN void  dmplexglobalvectorview_(DM dm,PetscViewer viewer,DM sectiondm,Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLOBJECT(sectiondm);
CHKFORTRANNULLOBJECT(vec);
*ierr = DMPlexGlobalVectorView(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),
	(DM)PetscToPointer((sectiondm) ),
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  dmplexlocalvectorview_(DM dm,PetscViewer viewer,DM sectiondm,Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLOBJECT(sectiondm);
CHKFORTRANNULLOBJECT(vec);
*ierr = DMPlexLocalVectorView(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),
	(DM)PetscToPointer((sectiondm) ),
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  dmplextopologyload_(DM dm,PetscViewer viewer,PetscSF *globalToLocalPointSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
PetscBool globalToLocalPointSF_null = !*(void**) globalToLocalPointSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(globalToLocalPointSF);
*ierr = DMPlexTopologyLoad(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),globalToLocalPointSF);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! globalToLocalPointSF_null && !*(void**) globalToLocalPointSF) * (void **) globalToLocalPointSF = (void *)-2;
}
PETSC_EXTERN void  dmplexcoordinatesload_(DM dm,PetscViewer viewer,PetscSF globalToLocalPointSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLOBJECT(globalToLocalPointSF);
*ierr = DMPlexCoordinatesLoad(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),
	(PetscSF)PetscToPointer((globalToLocalPointSF) ));
}
PETSC_EXTERN void  dmplexlabelsload_(DM dm,PetscViewer viewer,PetscSF globalToLocalPointSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLOBJECT(globalToLocalPointSF);
*ierr = DMPlexLabelsLoad(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),
	(PetscSF)PetscToPointer((globalToLocalPointSF) ));
}
PETSC_EXTERN void  dmplexsectionload_(DM dm,PetscViewer viewer,DM sectiondm,PetscSF globalToLocalPointSF,PetscSF *globalDofSF,PetscSF *localDofSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLOBJECT(sectiondm);
CHKFORTRANNULLOBJECT(globalToLocalPointSF);
PetscBool globalDofSF_null = !*(void**) globalDofSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(globalDofSF);
PetscBool localDofSF_null = !*(void**) localDofSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(localDofSF);
*ierr = DMPlexSectionLoad(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),
	(DM)PetscToPointer((sectiondm) ),
	(PetscSF)PetscToPointer((globalToLocalPointSF) ),globalDofSF,localDofSF);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! globalDofSF_null && !*(void**) globalDofSF) * (void **) globalDofSF = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! localDofSF_null && !*(void**) localDofSF) * (void **) localDofSF = (void *)-2;
}
PETSC_EXTERN void  dmplexglobalvectorload_(DM dm,PetscViewer viewer,DM sectiondm,PetscSF sf,Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLOBJECT(sectiondm);
CHKFORTRANNULLOBJECT(sf);
CHKFORTRANNULLOBJECT(vec);
*ierr = DMPlexGlobalVectorLoad(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),
	(DM)PetscToPointer((sectiondm) ),
	(PetscSF)PetscToPointer((sf) ),
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  dmplexlocalvectorload_(DM dm,PetscViewer viewer,DM sectiondm,PetscSF sf,Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLOBJECT(sectiondm);
CHKFORTRANNULLOBJECT(sf);
CHKFORTRANNULLOBJECT(vec);
*ierr = DMPlexLocalVectorLoad(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),
	(DM)PetscToPointer((sectiondm) ),
	(PetscSF)PetscToPointer((sf) ),
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  dmplexgetsubdomainsection_(DM dm,PetscSection *subsection, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool subsection_null = !*(void**) subsection ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subsection);
*ierr = DMPlexGetSubdomainSection(
	(DM)PetscToPointer((dm) ),subsection);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subsection_null && !*(void**) subsection) * (void **) subsection = (void *)-2;
}
PETSC_EXTERN void  dmplexgetchart_(DM dm,PetscInt *pStart,PetscInt *pEnd, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(pStart);
CHKFORTRANNULLINTEGER(pEnd);
*ierr = DMPlexGetChart(
	(DM)PetscToPointer((dm) ),pStart,pEnd);
}
PETSC_EXTERN void  dmplexsetchart_(DM dm,PetscInt *pStart,PetscInt *pEnd, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetChart(
	(DM)PetscToPointer((dm) ),*pStart,*pEnd);
}
PETSC_EXTERN void  dmplexgetconesize_(DM dm,PetscInt *p,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(size);
*ierr = DMPlexGetConeSize(
	(DM)PetscToPointer((dm) ),*p,size);
}
PETSC_EXTERN void  dmplexsetconesize_(DM dm,PetscInt *p,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetConeSize(
	(DM)PetscToPointer((dm) ),*p,*size);
}
PETSC_EXTERN void  dmplexgetconetuple_(DM dm,IS p,PetscSection *pConesSection,IS *pCones, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(p);
PetscBool pConesSection_null = !*(void**) pConesSection ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pConesSection);
PetscBool pCones_null = !*(void**) pCones ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pCones);
*ierr = DMPlexGetConeTuple(
	(DM)PetscToPointer((dm) ),
	(IS)PetscToPointer((p) ),pConesSection,pCones);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pConesSection_null && !*(void**) pConesSection) * (void **) pConesSection = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pCones_null && !*(void**) pCones) * (void **) pCones = (void *)-2;
}
PETSC_EXTERN void  dmplexgetconerecursivevertices_(DM dm,IS points,IS *expandedPoints, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(points);
PetscBool expandedPoints_null = !*(void**) expandedPoints ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(expandedPoints);
*ierr = DMPlexGetConeRecursiveVertices(
	(DM)PetscToPointer((dm) ),
	(IS)PetscToPointer((points) ),expandedPoints);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! expandedPoints_null && !*(void**) expandedPoints) * (void **) expandedPoints = (void *)-2;
}
PETSC_EXTERN void  dmplexgetconerecursive_(DM dm,IS points,PetscInt *depth,IS *expandedPoints[],PetscSection *sections[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(points);
CHKFORTRANNULLINTEGER(depth);
CHKFORTRANNULLOBJECT(expandedPoints);
CHKFORTRANNULLOBJECT(sections);
*ierr = DMPlexGetConeRecursive(
	(DM)PetscToPointer((dm) ),
	(IS)PetscToPointer((points) ),depth,expandedPoints,sections);
}
PETSC_EXTERN void  dmplexrestoreconerecursive_(DM dm,IS points,PetscInt *depth,IS *expandedPoints[],PetscSection *sections[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(points);
CHKFORTRANNULLINTEGER(depth);
CHKFORTRANNULLOBJECT(expandedPoints);
CHKFORTRANNULLOBJECT(sections);
*ierr = DMPlexRestoreConeRecursive(
	(DM)PetscToPointer((dm) ),
	(IS)PetscToPointer((points) ),depth,expandedPoints,sections);
}
PETSC_EXTERN void  dmplexsetcone_(DM dm,PetscInt *p, PetscInt cone[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(cone);
*ierr = DMPlexSetCone(
	(DM)PetscToPointer((dm) ),*p,cone);
}
PETSC_EXTERN void  dmplexsetconeorientation_(DM dm,PetscInt *p, PetscInt coneOrientation[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(coneOrientation);
*ierr = DMPlexSetConeOrientation(
	(DM)PetscToPointer((dm) ),*p,coneOrientation);
}
PETSC_EXTERN void  dmplexinsertcone_(DM dm,PetscInt *p,PetscInt *conePos,PetscInt *conePoint, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexInsertCone(
	(DM)PetscToPointer((dm) ),*p,*conePos,*conePoint);
}
PETSC_EXTERN void  dmplexinsertconeorientation_(DM dm,PetscInt *p,PetscInt *conePos,PetscInt *coneOrientation, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexInsertConeOrientation(
	(DM)PetscToPointer((dm) ),*p,*conePos,*coneOrientation);
}
PETSC_EXTERN void  dmplexgetsupportsize_(DM dm,PetscInt *p,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(size);
*ierr = DMPlexGetSupportSize(
	(DM)PetscToPointer((dm) ),*p,size);
}
PETSC_EXTERN void  dmplexsetsupportsize_(DM dm,PetscInt *p,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetSupportSize(
	(DM)PetscToPointer((dm) ),*p,*size);
}
PETSC_EXTERN void  dmplexsetsupport_(DM dm,PetscInt *p, PetscInt support[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(support);
*ierr = DMPlexSetSupport(
	(DM)PetscToPointer((dm) ),*p,support);
}
PETSC_EXTERN void  dmplexinsertsupport_(DM dm,PetscInt *p,PetscInt *supportPos,PetscInt *supportPoint, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexInsertSupport(
	(DM)PetscToPointer((dm) ),*p,*supportPos,*supportPoint);
}
PETSC_EXTERN void  dmplexgetmaxsizes_(DM dm,PetscInt *maxConeSize,PetscInt *maxSupportSize, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(maxConeSize);
CHKFORTRANNULLINTEGER(maxSupportSize);
*ierr = DMPlexGetMaxSizes(
	(DM)PetscToPointer((dm) ),maxConeSize,maxSupportSize);
}
PETSC_EXTERN void  dmplexsymmetrize_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSymmetrize(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmplexstratify_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexStratify(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmplexcomputecelltypes_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexComputeCellTypes(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmplexequal_(DM dmA,DM dmB,PetscBool *equal, int *ierr)
{
CHKFORTRANNULLOBJECT(dmA);
CHKFORTRANNULLOBJECT(dmB);
*ierr = DMPlexEqual(
	(DM)PetscToPointer((dmA) ),
	(DM)PetscToPointer((dmB) ),equal);
}
PETSC_EXTERN void  dmplexgetnumfacevertices_(DM dm,PetscInt *cellDim,PetscInt *numCorners,PetscInt *numFaceVertices, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(numFaceVertices);
*ierr = DMPlexGetNumFaceVertices(
	(DM)PetscToPointer((dm) ),*cellDim,*numCorners,numFaceVertices);
}
PETSC_EXTERN void  dmplexgetdepthlabel_(DM dm,DMLabel *depthLabel, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool depthLabel_null = !*(void**) depthLabel ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(depthLabel);
*ierr = DMPlexGetDepthLabel(
	(DM)PetscToPointer((dm) ),depthLabel);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! depthLabel_null && !*(void**) depthLabel) * (void **) depthLabel = (void *)-2;
}
PETSC_EXTERN void  dmplexgetdepth_(DM dm,PetscInt *depth, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(depth);
*ierr = DMPlexGetDepth(
	(DM)PetscToPointer((dm) ),depth);
}
PETSC_EXTERN void  dmplexgetdepthstratum_(DM dm,PetscInt *depth,PetscInt *start,PetscInt *end, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(start);
CHKFORTRANNULLINTEGER(end);
*ierr = DMPlexGetDepthStratum(
	(DM)PetscToPointer((dm) ),*depth,start,end);
}
PETSC_EXTERN void  dmplexgetheightstratum_(DM dm,PetscInt *height,PetscInt *start,PetscInt *end, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(start);
CHKFORTRANNULLINTEGER(end);
*ierr = DMPlexGetHeightStratum(
	(DM)PetscToPointer((dm) ),*height,start,end);
}
PETSC_EXTERN void  dmplexgetpointdepth_(DM dm,PetscInt *point,PetscInt *depth, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(depth);
*ierr = DMPlexGetPointDepth(
	(DM)PetscToPointer((dm) ),*point,depth);
}
PETSC_EXTERN void  dmplexgetpointheight_(DM dm,PetscInt *point,PetscInt *height, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(height);
*ierr = DMPlexGetPointHeight(
	(DM)PetscToPointer((dm) ),*point,height);
}
PETSC_EXTERN void  dmplexgetcelltypelabel_(DM dm,DMLabel *celltypeLabel, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool celltypeLabel_null = !*(void**) celltypeLabel ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(celltypeLabel);
*ierr = DMPlexGetCellTypeLabel(
	(DM)PetscToPointer((dm) ),celltypeLabel);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! celltypeLabel_null && !*(void**) celltypeLabel) * (void **) celltypeLabel = (void *)-2;
}
PETSC_EXTERN void  dmplexgetcelltype_(DM dm,PetscInt *cell,DMPolytopeType *celltype, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexGetCellType(
	(DM)PetscToPointer((dm) ),*cell,celltype);
}
PETSC_EXTERN void  dmplexsetcelltype_(DM dm,PetscInt *cell,DMPolytopeType *celltype, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetCellType(
	(DM)PetscToPointer((dm) ),*cell,*celltype);
}
PETSC_EXTERN void  dmplexgetconesection_(DM dm,PetscSection *section, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool section_null = !*(void**) section ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(section);
*ierr = DMPlexGetConeSection(
	(DM)PetscToPointer((dm) ),section);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! section_null && !*(void**) section) * (void **) section = (void *)-2;
}
PETSC_EXTERN void  dmplexgetsupportsection_(DM dm,PetscSection *section, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool section_null = !*(void**) section ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(section);
*ierr = DMPlexGetSupportSection(
	(DM)PetscToPointer((dm) ),section);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! section_null && !*(void**) section) * (void **) section = (void *)-2;
}
PETSC_EXTERN void  dmplexsetclosurepermutationtensor_(DM dm,PetscInt *point,PetscSection section, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(section);
*ierr = DMPlexSetClosurePermutationTensor(
	(DM)PetscToPointer((dm) ),*point,
	(PetscSection)PetscToPointer((section) ));
}
PETSC_EXTERN void  dmplexgetvtkcellheight_(DM dm,PetscInt *cellHeight, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(cellHeight);
*ierr = DMPlexGetVTKCellHeight(
	(DM)PetscToPointer((dm) ),cellHeight);
}
PETSC_EXTERN void  dmplexsetvtkcellheight_(DM dm,PetscInt *cellHeight, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetVTKCellHeight(
	(DM)PetscToPointer((dm) ),*cellHeight);
}
PETSC_EXTERN void  dmplexgetcelltypestratum_(DM dm,DMPolytopeType *ct,PetscInt *start,PetscInt *end, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(start);
CHKFORTRANNULLINTEGER(end);
*ierr = DMPlexGetCellTypeStratum(
	(DM)PetscToPointer((dm) ),*ct,start,end);
}
PETSC_EXTERN void  dmplexgetdepthstratumglobalsize_(DM dm,PetscInt *depth,PetscInt *gsize, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(gsize);
*ierr = DMPlexGetDepthStratumGlobalSize(
	(DM)PetscToPointer((dm) ),*depth,gsize);
}
PETSC_EXTERN void  dmplexcreatecellnumbering_(DM dm,PetscBool *includeAll,IS *globalCellNumbers, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool globalCellNumbers_null = !*(void**) globalCellNumbers ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(globalCellNumbers);
*ierr = DMPlexCreateCellNumbering(
	(DM)PetscToPointer((dm) ),*includeAll,globalCellNumbers);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! globalCellNumbers_null && !*(void**) globalCellNumbers) * (void **) globalCellNumbers = (void *)-2;
}
PETSC_EXTERN void  dmplexgetcellnumbering_(DM dm,IS *globalCellNumbers, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool globalCellNumbers_null = !*(void**) globalCellNumbers ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(globalCellNumbers);
*ierr = DMPlexGetCellNumbering(
	(DM)PetscToPointer((dm) ),globalCellNumbers);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! globalCellNumbers_null && !*(void**) globalCellNumbers) * (void **) globalCellNumbers = (void *)-2;
}
PETSC_EXTERN void  dmplexgetvertexnumbering_(DM dm,IS *globalVertexNumbers, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool globalVertexNumbers_null = !*(void**) globalVertexNumbers ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(globalVertexNumbers);
*ierr = DMPlexGetVertexNumbering(
	(DM)PetscToPointer((dm) ),globalVertexNumbers);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! globalVertexNumbers_null && !*(void**) globalVertexNumbers) * (void **) globalVertexNumbers = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatepointnumbering_(DM dm,IS *globalPointNumbers, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool globalPointNumbers_null = !*(void**) globalPointNumbers ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(globalPointNumbers);
*ierr = DMPlexCreatePointNumbering(
	(DM)PetscToPointer((dm) ),globalPointNumbers);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! globalPointNumbers_null && !*(void**) globalPointNumbers) * (void **) globalPointNumbers = (void *)-2;
}
PETSC_EXTERN void  dmplexcreateedgenumbering_(DM dm,IS *globalEdgeNumbers, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool globalEdgeNumbers_null = !*(void**) globalEdgeNumbers ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(globalEdgeNumbers);
*ierr = DMPlexCreateEdgeNumbering(
	(DM)PetscToPointer((dm) ),globalEdgeNumbers);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! globalEdgeNumbers_null && !*(void**) globalEdgeNumbers) * (void **) globalEdgeNumbers = (void *)-2;
}
PETSC_EXTERN void  dmplexcreaterankfield_(DM dm,Vec *ranks, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool ranks_null = !*(void**) ranks ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ranks);
*ierr = DMPlexCreateRankField(
	(DM)PetscToPointer((dm) ),ranks);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ranks_null && !*(void**) ranks) * (void **) ranks = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatelabelfield_(DM dm,DMLabel label,Vec *val, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
PetscBool val_null = !*(void**) val ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(val);
*ierr = DMPlexCreateLabelField(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ),val);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! val_null && !*(void**) val) * (void **) val = (void *)-2;
}
PETSC_EXTERN void  dmplexchecksymmetry_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCheckSymmetry(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmplexcheckskeleton_(DM dm,PetscInt *cellHeight, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCheckSkeleton(
	(DM)PetscToPointer((dm) ),*cellHeight);
}
PETSC_EXTERN void  dmplexcheckfaces_(DM dm,PetscInt *cellHeight, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCheckFaces(
	(DM)PetscToPointer((dm) ),*cellHeight);
}
PETSC_EXTERN void  dmplexcheckgeometry_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCheckGeometry(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmplexcheckpointsf_(DM dm,PetscSF pointSF,PetscBool *allowExtraRoots, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(pointSF);
*ierr = DMPlexCheckPointSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((pointSF) ),*allowExtraRoots);
}
PETSC_EXTERN void  dmplexcheckorphanvertices_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCheckOrphanVertices(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmplexcheck_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCheck(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmplexcheckcellshape_(DM dm,PetscBool *output,PetscReal *condLimit, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCheckCellShape(
	(DM)PetscToPointer((dm) ),*output,*condLimit);
}
PETSC_EXTERN void  dmplexcomputeorthogonalquality_(DM dm,PetscFV fv,PetscReal *atol,Vec *OrthQual,DMLabel *OrthQualLabel, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(fv);
PetscBool OrthQual_null = !*(void**) OrthQual ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(OrthQual);
PetscBool OrthQualLabel_null = !*(void**) OrthQualLabel ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(OrthQualLabel);
*ierr = DMPlexComputeOrthogonalQuality(
	(DM)PetscToPointer((dm) ),
	(PetscFV)PetscToPointer((fv) ),*atol,OrthQual,OrthQualLabel);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! OrthQual_null && !*(void**) OrthQual) * (void **) OrthQual = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! OrthQualLabel_null && !*(void**) OrthQualLabel) * (void **) OrthQualLabel = (void *)-2;
}
PETSC_EXTERN void  dmplexgetregularrefinement_(DM dm,PetscBool *regular, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexGetRegularRefinement(
	(DM)PetscToPointer((dm) ),regular);
}
PETSC_EXTERN void  dmplexsetregularrefinement_(DM dm,PetscBool *regular, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetRegularRefinement(
	(DM)PetscToPointer((dm) ),*regular);
}
PETSC_EXTERN void  dmplexgetanchors_(DM dm,PetscSection *anchorSection,IS *anchorIS, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool anchorSection_null = !*(void**) anchorSection ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(anchorSection);
PetscBool anchorIS_null = !*(void**) anchorIS ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(anchorIS);
*ierr = DMPlexGetAnchors(
	(DM)PetscToPointer((dm) ),anchorSection,anchorIS);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! anchorSection_null && !*(void**) anchorSection) * (void **) anchorSection = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! anchorIS_null && !*(void**) anchorIS) * (void **) anchorIS = (void *)-2;
}
PETSC_EXTERN void  dmplexsetanchors_(DM dm,PetscSection anchorSection,IS anchorIS, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(anchorSection);
CHKFORTRANNULLOBJECT(anchorIS);
*ierr = DMPlexSetAnchors(
	(DM)PetscToPointer((dm) ),
	(PetscSection)PetscToPointer((anchorSection) ),
	(IS)PetscToPointer((anchorIS) ));
}
PETSC_EXTERN void  dmplexmonitorthroughput_(DM dm,void*dummy, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexMonitorThroughput(
	(DM)PetscToPointer((dm) ),dummy);
}
#if defined(__cplusplus)
}
#endif
