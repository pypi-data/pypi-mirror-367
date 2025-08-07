#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* characteristic.c */
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

#include "petsccharacteristic.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define characteristicsettype_ CHARACTERISTICSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define characteristicsettype_ characteristicsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define characteristicsetup_ CHARACTERISTICSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define characteristicsetup_ characteristicsetup
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  characteristicsettype_(Characteristic c,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(c);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = CharacteristicSetType(
	(Characteristic)PetscToPointer((c) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  characteristicsetup_(Characteristic c, int *ierr)
{
CHKFORTRANNULLOBJECT(c);
*ierr = CharacteristicSetUp(
	(Characteristic)PetscToPointer((c) ));
}
#if defined(__cplusplus)
}
#endif
