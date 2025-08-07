#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* optionsyaml.c */
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

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsinsertstringyaml_ PETSCOPTIONSINSERTSTRINGYAML
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsinsertstringyaml_ petscoptionsinsertstringyaml
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscoptionsinsertfileyaml_ PETSCOPTIONSINSERTFILEYAML
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscoptionsinsertfileyaml_ petscoptionsinsertfileyaml
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscoptionsinsertstringyaml_(PetscOptions options, char in_str[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for in_str */
  FIXCHAR(in_str,cl0,_cltmp0);
*ierr = PetscOptionsInsertStringYAML(
	(PetscOptions)PetscToPointer((options) ),_cltmp0);
  FREECHAR(in_str,_cltmp0);
}
PETSC_EXTERN void  petscoptionsinsertfileyaml_(MPI_Fint * comm,PetscOptions options, char file[],PetscBool *require, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(options);
/* insert Fortran-to-C conversion for file */
  FIXCHAR(file,cl0,_cltmp0);
*ierr = PetscOptionsInsertFileYAML(
	MPI_Comm_f2c(*(comm)),
	(PetscOptions)PetscToPointer((options) ),_cltmp0,*require);
  FREECHAR(file,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
