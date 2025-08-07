#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* sliced.c */
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

#include "petscdmsliced.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmslicedsetghosts_ DMSLICEDSETGHOSTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmslicedsetghosts_ dmslicedsetghosts
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmslicedsetpreallocation_ DMSLICEDSETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmslicedsetpreallocation_ dmslicedsetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmslicedsetblockfills_ DMSLICEDSETBLOCKFILLS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmslicedsetblockfills_ dmslicedsetblockfills
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmslicedcreate_ DMSLICEDCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmslicedcreate_ dmslicedcreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmslicedsetghosts_(DM dm,PetscInt *bs,PetscInt *nlocal,PetscInt *Nghosts, PetscInt ghosts[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(ghosts);
*ierr = DMSlicedSetGhosts(
	(DM)PetscToPointer((dm) ),*bs,*nlocal,*Nghosts,ghosts);
}
PETSC_EXTERN void  dmslicedsetpreallocation_(DM dm,PetscInt *d_nz, PetscInt d_nnz[],PetscInt *o_nz, PetscInt o_nnz[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(d_nnz);
CHKFORTRANNULLINTEGER(o_nnz);
*ierr = DMSlicedSetPreallocation(
	(DM)PetscToPointer((dm) ),*d_nz,d_nnz,*o_nz,o_nnz);
}
PETSC_EXTERN void  dmslicedsetblockfills_(DM dm, PetscInt dfill[], PetscInt ofill[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(dfill);
CHKFORTRANNULLINTEGER(ofill);
*ierr = DMSlicedSetBlockFills(
	(DM)PetscToPointer((dm) ),dfill,ofill);
}
PETSC_EXTERN void  dmslicedcreate_(MPI_Fint * comm,PetscInt *bs,PetscInt *nlocal,PetscInt *Nghosts, PetscInt ghosts[], PetscInt d_nnz[], PetscInt o_nnz[],DM *dm, int *ierr)
{
CHKFORTRANNULLINTEGER(ghosts);
CHKFORTRANNULLINTEGER(d_nnz);
CHKFORTRANNULLINTEGER(o_nnz);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSlicedCreate(
	MPI_Comm_f2c(*(comm)),*bs,*nlocal,*Nghosts,ghosts,d_nnz,o_nnz,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
