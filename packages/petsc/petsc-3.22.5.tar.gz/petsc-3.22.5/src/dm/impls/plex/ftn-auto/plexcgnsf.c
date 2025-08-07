#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexcgns.c */
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
#define dmplexcreatecgns_ DMPLEXCREATECGNS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatecgns_ dmplexcreatecgns
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexcreatecgns_(MPI_Fint * comm,PetscInt *cgid,PetscBool *interpolate,DM *dm, int *ierr)
{
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateCGNS(
	MPI_Comm_f2c(*(comm)),*cgid,*interpolate,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
