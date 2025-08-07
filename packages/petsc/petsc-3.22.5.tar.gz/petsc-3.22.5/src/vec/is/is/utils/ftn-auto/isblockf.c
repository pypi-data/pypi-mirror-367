#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* isblock.c */
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

#include "petscis.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscompressindicesgeneral_ ISCOMPRESSINDICESGENERAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscompressindicesgeneral_ iscompressindicesgeneral
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isexpandindicesgeneral_ ISEXPANDINDICESGENERAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isexpandindicesgeneral_ isexpandindicesgeneral
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  iscompressindicesgeneral_(PetscInt *n,PetscInt *nkeys,PetscInt *bs,PetscInt *imax, IS is_in[],IS is_out[], int *ierr)
{
PetscBool is_in_null = !*(void**) is_in ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is_in);
PetscBool is_out_null = !*(void**) is_out ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is_out);
*ierr = ISCompressIndicesGeneral(*n,*nkeys,*bs,*imax,is_in,is_out);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_in_null && !*(void**) is_in) * (void **) is_in = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_out_null && !*(void**) is_out) * (void **) is_out = (void *)-2;
}
PETSC_EXTERN void  isexpandindicesgeneral_(PetscInt *n,PetscInt *nkeys,PetscInt *bs,PetscInt *imax, IS is_in[],IS is_out[], int *ierr)
{
PetscBool is_in_null = !*(void**) is_in ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is_in);
PetscBool is_out_null = !*(void**) is_out ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is_out);
*ierr = ISExpandIndicesGeneral(*n,*nkeys,*bs,*imax,is_in,is_out);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_in_null && !*(void**) is_in) * (void **) is_in = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_out_null && !*(void**) is_out) * (void **) is_out = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
