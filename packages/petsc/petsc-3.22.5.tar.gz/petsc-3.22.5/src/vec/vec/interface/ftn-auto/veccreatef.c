#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* veccreate.c */
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

#include "petscvec.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define veccreate_ VECCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define veccreate_ veccreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define veccreatefromoptions_ VECCREATEFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define veccreatefromoptions_ veccreatefromoptions
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  veccreate_(MPI_Fint * comm,Vec *vec, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(vec);
 PetscBool vec_null = !*(void**) vec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vec);
*ierr = VecCreate(
	MPI_Comm_f2c(*(comm)),vec);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vec_null && !*(void**) vec) * (void **) vec = (void *)-2;
}
PETSC_EXTERN void  veccreatefromoptions_(MPI_Fint * comm, char *prefix,PetscInt *bs,PetscInt *m,PetscInt *n,Vec *vec, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool vec_null = !*(void**) vec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vec);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = VecCreateFromOptions(
	MPI_Comm_f2c(*(comm)),_cltmp0,*bs,*m,*n,vec);
  FREECHAR(prefix,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vec_null && !*(void**) vec) * (void **) vec = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
