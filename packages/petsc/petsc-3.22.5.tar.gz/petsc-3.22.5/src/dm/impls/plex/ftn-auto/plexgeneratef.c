#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexgenerate.c */
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
#define dmplexinvertcell_ DMPLEXINVERTCELL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexinvertcell_ dmplexinvertcell
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexreordercell_ DMPLEXREORDERCELL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexreordercell_ dmplexreordercell
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgenerate_ DMPLEXGENERATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgenerate_ dmplexgenerate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexinvertcell_(DMPolytopeType *cellType,PetscInt cone[], int *ierr)
{
CHKFORTRANNULLINTEGER(cone);
*ierr = DMPlexInvertCell(*cellType,cone);
}
PETSC_EXTERN void  dmplexreordercell_(DM dm,PetscInt *cell,PetscInt cone[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(cone);
*ierr = DMPlexReorderCell(
	(DM)PetscToPointer((dm) ),*cell,cone);
}
PETSC_EXTERN void  dmplexgenerate_(DM boundary, char name[],PetscBool *interpolate,DM *mesh, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(boundary);
PetscBool mesh_null = !*(void**) mesh ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mesh);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMPlexGenerate(
	(DM)PetscToPointer((boundary) ),_cltmp0,*interpolate,mesh);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mesh_null && !*(void**) mesh) * (void **) mesh = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
