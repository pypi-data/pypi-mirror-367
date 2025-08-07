#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* aomapping.c */
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

#include "petscao.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aomappinghasapplicationindex_ AOMAPPINGHASAPPLICATIONINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aomappinghasapplicationindex_ aomappinghasapplicationindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aomappinghaspetscindex_ AOMAPPINGHASPETSCINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aomappinghaspetscindex_ aomappinghaspetscindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aocreatemapping_ AOCREATEMAPPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aocreatemapping_ aocreatemapping
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define aocreatemappingis_ AOCREATEMAPPINGIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define aocreatemappingis_ aocreatemappingis
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  aomappinghasapplicationindex_(AO ao,PetscInt *idex,PetscBool *hasIndex, int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
*ierr = AOMappingHasApplicationIndex(
	(AO)PetscToPointer((ao) ),*idex,hasIndex);
}
PETSC_EXTERN void  aomappinghaspetscindex_(AO ao,PetscInt *idex,PetscBool *hasIndex, int *ierr)
{
CHKFORTRANNULLOBJECT(ao);
*ierr = AOMappingHasPetscIndex(
	(AO)PetscToPointer((ao) ),*idex,hasIndex);
}
PETSC_EXTERN void  aocreatemapping_(MPI_Fint * comm,PetscInt *napp, PetscInt myapp[], PetscInt mypetsc[],AO *aoout, int *ierr)
{
CHKFORTRANNULLINTEGER(myapp);
CHKFORTRANNULLINTEGER(mypetsc);
PetscBool aoout_null = !*(void**) aoout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(aoout);
*ierr = AOCreateMapping(
	MPI_Comm_f2c(*(comm)),*napp,myapp,mypetsc,aoout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! aoout_null && !*(void**) aoout) * (void **) aoout = (void *)-2;
}
PETSC_EXTERN void  aocreatemappingis_(IS isapp,IS ispetsc,AO *aoout, int *ierr)
{
CHKFORTRANNULLOBJECT(isapp);
CHKFORTRANNULLOBJECT(ispetsc);
PetscBool aoout_null = !*(void**) aoout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(aoout);
*ierr = AOCreateMappingIS(
	(IS)PetscToPointer((isapp) ),
	(IS)PetscToPointer((ispetsc) ),aoout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! aoout_null && !*(void**) aoout) * (void **) aoout = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
